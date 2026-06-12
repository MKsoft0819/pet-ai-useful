import streamlit as st
from google import genai

# --- ページ設定（ポップなタイトルと絵文字） ---
st.set_page_config(
    page_title="AI Pet Meal Planner 🐾",
    layout="centered", # 中央寄せ
    initial_sidebar_state="collapsed" # 最初からサイドバーを閉じておく
)

# --- 魔法の隠し金庫（Secrets）からAPIキーを読み込む ---
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# --- ポップなデザインにするためのカスタムCSS ---
st.markdown("""
    <style>
    /* 全体のフォントを少し丸く、背景を優しく */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        background-color: #fdfdfd;
    }
    /* タイトルのデザイン */
    .main-title {
        color: #ff823a;
        font-size: 3rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    /* 入力エリアのカード風デザイン */
    .stSelectbox, .stNumberInput {
        background-color: #ffffff;
        border-radius: 15px;
    }
    /* ボタンをポップな色に（パープル） */
    div.stButton > button {
        background-color: #bc84ee !important;
        color: white !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(188, 132, 238, 0.4);
    }
    /* サイドバーを完全に非表示にする魔法 */
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- ヘッダーエリア ---
st.markdown('<p class="main-title">🐾 AI Pet Meal Planner</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b;">AIと一緒に、うちの子にぴったりのごはん量を見つけよう！</p>', unsafe_allow_html=True)

st.write("---")

# --- 入力エリア（サイドバーの代わりに3つの列で配置！） ---
col1, col2, col3 = st.columns(3)

with col1:
    pet_type = st.selectbox("種類 🐶🐱", ["犬", "猫"])

with col2:
    weight = st.number_input("体重 (kg) ⚖️", min_value=0.1, value=5.0, step=0.1)

with col3:
    activity_level = st.selectbox("活動量 🏃", ["低い", "普通", "高い"])

# --- 追加情報エリア ---
st.write("")
memo = st.text_input("AIへのメッセージ（例：最近少し太り気味、食欲旺盛！） 💬", placeholder="何か気になることがあれば教えてね")

# --- 計算・AIアドバイス実行ボタン ---
st.write("")
if st.button("AIに相談して計算する ✨"):
    # AIへの依頼文（プロンプト）
    prompt = f"""
    あなたは親切な獣医です。以下の情報を元に、{pet_type}の1日あたりの推定給餌量(グラム)を計算し、
    飼い主さんへ明るくポップなアドバイスをしてください。
    
    情報：
    - 体重: {weight}kg
    - 活動量: {activity_level}
    - 飼い主からのメモ: {memo}
    
    回答の構成：
    1. 推定される1日のごはんの量（グラム）を大きく提示
    2. その理由を簡単に説明
    3. 飼い主さんとペットが幸せになれるような一言アドバイス
    """
    
    with st.spinner("AIが一生懸命考えています... 🧠🎨"):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # 結果表示（ポップな装飾枠）
            st.success("### 🥗 AI獣医からの回答")
            st.markdown(response.text)
            st.balloons() # お祝いの風船を飛ばす！
            
        except Exception as e:
            st.error(f"エラーが発生しました：{e}")

# --- フッター ---
st.write("---")
st.caption("※この計算は目安です。体調に合わせて調整してあげてくださいね。")