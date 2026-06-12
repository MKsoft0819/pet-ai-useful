import streamlit as st
from google import genai

# --- ページ設定 ---
st.set_page_config(
    page_title="AI Pet Meal Planner 🐾",
    layout="centered", # 中央寄せ
    initial_sidebar_state="collapsed" # サイドバーは最初から閉じる
)

# --- 魔法の隠し金庫（Secrets）からAPIキーを読み込む ---
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# --- ポップなカスタムCSS ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        background-color: #fdfdfd;
    }
    .main-title {
        color: #ff823a;
        font-size: 3rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stSelectbox, .stNumberInput {
        background-color: #ffffff;
        border-radius: 15px;
    }
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
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- ヘッダーエリア ---
st.markdown('<p class="main-title">🐾 AI Pet Meal Planner</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b;">AIと一緒に、うちの子にぴったりのごはん量を見つけよう！</p>', unsafe_allow_html=True)

st.write("---")

# --- 入力エリア（1段目：基本情報 3列） ---
col1, col2, col3 = st.columns(3)

with col1:
    pet_type = st.selectbox("種類 🐶🐱", ["犬", "猫"])

with col2:
    weight = st.number_input("体重 (kg) ⚖️", min_value=0.1, value=5.0, step=0.1)

with col3:
    activity_level = st.selectbox("活動量 🏃", ["低い", "普通", "高い"])

# --- 入力エリア（2段目：年齢 と 体の状態 2列） ---
st.write("")
col4, col5 = st.columns(2)

with col4:
    age_group = st.selectbox(
        "年齢・ライフステージ 🎂", 
        [
            "生後4ヶ月未満（幼齢期） 🍼", 
            "生後4ヶ月〜1歳まで（成長期） 🌱", 
            "成犬・成猫（1歳〜） 🐕🐈", 
            "シニア（7歳〜） 👴👵", 
            "ハイシニア（11歳〜） 🌟"
        ]
    )

with col5:
    # プランA：妊娠前半・後半を細かく分けました！
    pet_status = st.selectbox(
        "体の状態 🩺", 
        [
            "手術していない（未手術）", 
            "手術している（避妊・去勢済み）",
            "妊娠前半（交配〜4・5週目頃：いつも通りの時期） 🤰",
            "妊娠後半（5・6週目〜出産まで：赤ちゃん急成長期！） 🔥🤰",
            "授乳中（子育て中！） 🍼✨"
        ]
    )

# --- 入力エリア（3段目：ごはんのカロリー） ---
st.write("")
food_calories = st.number_input(
    "今あげているフードのカロリー (100gあたり/kcal) 🍖", 
    min_value=100, 
    max_value=600, 
    value=350, 
    step=5
)

# --- 追加情報エリア ---
st.write("")
memo = st.text_input("AIへのメッセージ（例：最近少し太り気味、食欲旺盛！） 💬", placeholder="何か気になることがあれば教えてね")

# --- 計算・AIアドバイス実行ボタン ---
st.write("")
if st.button("AIに相談して計算する ✨"):
    # AIへの依頼文（妊娠前半・後半の獣医学的ルールを明記！）
    prompt = f"""
    あなたは親切な獣医です。以下の情報を元に、{pet_type}の1日あたりの推定給餌量(グラム)を計算し、
    飼い主さんへ明るくポップなアドバイスをしてください。
    
    情報：
    - ペットの種類: {pet_type}
    - 体重: {weight}kg
    - 活動量: {activity_level}
    - 年齢・ライフステージ: {age_group}
    - 体の状態: {pet_status}
    - 与えているフードのカロリー: 100gあたり {food_calories} kcal
    - 飼い主からのメモ: {memo}
    
    計算の考慮事項（獣医学の基準）：
    - ライフステージと「体の状態」を組み合わせてエネルギー要求量（DER）を厳密に計算してください。
    - 特に妊娠期の違いを厳密に区別してください：
      * 「妊娠前半」：胎児はまだ小さいため、必要なエネルギーは通常の未手術成犬/成猫とほぼ同じです（増やしすぎ注意）。
      * 「妊娠後半」：胎児が急激に成長するため、エネルギー要求量は通常の1.5〜2倍近くに跳ね上がります。ただし胃が圧迫されるため、食事を小分けにするアドバイスも必須です。
      * 「授乳中」：年間で最もエネルギーを消費する時期です。通常の2〜3倍以上のカロリーが必要になるため、給餌量を大幅に増やしてください。
    - 避妊・去勢済みの場合は太りやすいため、控えめに補正してください。