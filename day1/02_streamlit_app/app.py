# app.py
import streamlit as st
import ui                   # UIモジュール
import llm                  # LLMモジュール
import database             # データベースモジュール
import metrics              # 評価指標モジュール
import data                 # データモジュール
import torch
from transformers import pipeline
from config import MODEL_NAME
from huggingface_hub import HfFolder

# --- アプリケーション設定 ---
st.set_page_config(page_title="Gemma Chatbot", layout="wide")

# --- テーマ変更 --- 新規追加
if 'theme' not in st.session_state:
    st.session_state.theme = "theme-1"

with st.sidebar.expander("テーマ設定", expanded=False):
    choice = st.radio(
        "表示テーマを選択",
        ("theme-1", "theme-2"),
        index=0,
        key="theme_radio"
    )
    # 選択をセッションに反映
    st.session_state.theme = choice

if st.session_state.theme == "theme-2":
    st.markdown(
        """
        <style>
        /* メインコンテンツ全体 */
        [data-testid="stAppViewContainer"] {
            background-color: #1e1e1e !important;
            color: #f0f0f0 !important;
        }
        /* サイドバー */
        [data-testid="stSidebar"] {
            background-color: #252526 !important;
            color: #f0f0f0 !important;
        }
        /* 吹き出しやウィジェット */
        [data-testid="stBlock"] {
            background-color: #2e2e2e !important;
            color: #f0f0f0 !important;
        }
        /* テキスト要素 */
        .css-1d391kg, .css-10trblm, .css-18ni7ap {
            color: #f0f0f0 !important;
        }
        /* 入力欄 */
        textarea, input {
            background-color: #333333 !important;
            color: #f0f0f0 !important;
        }
        /* ボタン */
        button, .stButton>button {
            background-color: #3a3d41 !important;
            color: #f0f0f0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- 初期化処理 ---
# NLTKデータのダウンロード（初回起動時など）
metrics.initialize_nltk()

# データベースの初期化（テーブルが存在しない場合、作成）
database.init_db()

# データベースが空ならサンプルデータを投入
data.ensure_initial_data()

# LLMモデルのロード（キャッシュを利用）
# モデルをキャッシュして再利用
@st.cache_resource
def load_model():
    """LLMモデルをロードする"""
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"Using device: {device}") # 使用デバイスを表示
        pipe = pipeline(
            "text-generation",
            model=MODEL_NAME,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device=device
        )
        st.success(f"モデル '{MODEL_NAME}' の読み込みに成功しました。")
        return pipe
    except Exception as e:
        st.error(f"モデル '{MODEL_NAME}' の読み込みに失敗しました: {e}")
        st.error("GPUメモリ不足の可能性があります。不要なプロセスを終了するか、より小さいモデルの使用を検討してください。")
        return None
pipe = llm.load_model()

# --- Streamlit アプリケーション ---
st.title("🤖 Gemma 2 Chatbot with Feedback")
st.write("Gemmaモデルを使用したチャットボットです。回答に対してフィードバックを行えます。")
st.markdown("---")

# --- サイドバー ---
st.sidebar.title("ナビゲーション")
# セッション状態を使用して選択ページを保持
if 'page' not in st.session_state:
    st.session_state.page = "チャット" # デフォルトページ

page = st.sidebar.radio(
    "ページ選択",
    ["チャット", "履歴閲覧", "サンプルデータ管理"],
    key="page_selector",
    index=["チャット", "履歴閲覧", "サンプルデータ管理"].index(st.session_state.page), # 現在のページを選択状態にする
    on_change=lambda: setattr(st.session_state, 'page', st.session_state.page_selector) # 選択変更時に状態を更新
)


# --- メインコンテンツ ---
if st.session_state.page == "チャット":
    if pipe:
        ui.display_chat_page(pipe)
    else:
        st.error("チャット機能を利用できません。モデルの読み込みに失敗しました。")
elif st.session_state.page == "履歴閲覧":
    ui.display_history_page()
elif st.session_state.page == "サンプルデータ管理":
    ui.display_data_page()

# --- フッターなど（任意） ---
st.sidebar.markdown("---")
st.sidebar.info("開発者: [Your Name]")