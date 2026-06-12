import streamlit as st
from google import genai

# --- ページ設定 ---
st.set_page_config(
    page_title="AI Pet Meal Planner 🐾",
    layout="centered", 
    initial_sidebar_state="collapsed"
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
.stSelectbox, .stNumberInput, .stCheckbox {
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

# --- 1段目：基本情報 3列 ---
col1, col2, col3 = st.columns(3)
with col1:
    pet_type = st.selectbox("種類 🐶🐱", ["犬", "猫"])
with col2:
    weight = st.number_input("体重 (kg) ⚖️", min_value=0.1, value=5.0, step=0.1)
with col3:
    activity_level = st.selectbox("活動量 🏃", ["低い", "普通", "高い"])

# --- 2段目：年齢 と 体の状態 2列 ---
st.write("")
col4, col5 = st.columns(2)
with col4:
    age_group = st.selectbox(
        "年齢・ライフステージ 🎂", 
        ["生後4ヶ月未満（幼齢期） 🍼", "生後4ヶ月〜1歳まで（成長期） 🌱", "成犬・成猫（1歳〜） 🐕🐈", "シニア（7歳〜） 👴👵", "ハイシニア（11歳〜） 🌟"]
    )
with col5:
    pet_status = st.selectbox(
        "体の状態 🩺", 
        ["手術していない（未手術）", "手術している（避妊・去勢済み）", "妊娠前半 🤰", "妊娠後半 🔥🤰", "授乳中 🍼✨"]
    )

# --- 3段目：ごはんのカロリー ---
st.write("")
food_calories = st.number_input(
    "フードのカロリー (100gあたり/kcal) 🍖", 
    min_value=100, max_value=600, value=350, step=5
)

# --- ✨ 新機能：おやつ入力セクション（2つのボックスに進化！） ✨ ---
st.write("")
has_snacks = st.checkbox("今日はおやつをあげる？ 🦴")

snack_cal_per_100g = 0
snack_grams = 0

if has_snacks:
    st.info("おやつのパッケージの数字と、あげる量を入力してね！")
    # 2つの列に分けて横並びにスッキリ配置
    scol1, scol2 = st.columns(2)
    with scol1:
        snack_cal_per_100g = st.number_input(
            "おやつのカロリー (100gあたり/kcal) 🏷️", 
            min_value=50, max_value=800, value=300, step=5
        )
    with scol2:
        snack_grams = st.number_input(
            "今日あげるおやつの量 (g) ⚖️", 
            min_value=1, max_value=200, value=10, step=1
        )

# --- 追加情報エリア ---
st.write("")
memo = st.text_input("AIへのメッセージ 💬", placeholder="例：食欲がすごい、少しダイエット中など")

# --- 計算・AIアドバイス実行ボタン ---
st.write("")
if st.button("AIに相談して計算する ✨"):
    # AIへの依頼文（おやつの100gあたりカロリーとグラム数を渡して、AIに掛け算と引き算を両方やらせます！）
    prompt = f"""
あなたは親切な獣医です。以下の情報を元に、{pet_type}の1日あたりの推定給餌量(グラム)を計算してください。

情報：
- ペットの種類: {pet_type}
- 体重: {weight}kg
- 活動量: {activity_level}
- 年齢・ライフステージ: {age_group}
- 体の状態: {pet_status}
- フードのカロリー: 100gあたり {food_calories} kcal
- 今日あげるおやつのカロリー: 100gあたり {snack_cal_per_100g} kcal
- 今日あげるおやつの量: {snack_grams} g
- 飼い主からのメモ: {memo}

計算のステップ（重要）：
1. おやつの摂取カロリーをまず計算してください。（計算式: おやつの量({snack_grams}g) × (100gあたりのカロリー({snack_cal_per_100g}kcal) ÷ 100)）
2. ペットの1日の総必要エネルギー（DER）を算出してください。
3. 総必要エネルギーから、ステップ1で出したおやつ分のカロリーを差し引いてください。
4. 残りのエネルギーを「フード（100gあたり{food_calories}kcal）」で摂取する場合の、1日のグラム数を算出して提示してください。

回答の構成：
1. おやつ分を差し引いた、1日のごはんの量（グラム）を大きく提示。
2. 計算の内訳を分かりやすく解説（おやつの総カロリー、ペットの総必要カロリー、そこから引き算した残りのごはんの量）。
3. もしおやつのカロリーが1日の総カロリーの10%を超えていたら、健康のために優しく注意喚起してください。
4. 飼い主さんとペットが幸せになれるようなポップな一言。
"""
    
    with st.spinner("おやつのカロリーを計算して引き算しています... 🧠🍪⚖️"):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            st.success("### 🥗 AI獣医からの回答")
            st.markdown(response.text)
            st.balloons()
        except Exception as e:
            st.error(f"エラーが発生しました：{e}")

# --- フッター ---
st.write("---")
st.caption("※この計算は目安です。体調に合わせて調整してあげてくださいね。")