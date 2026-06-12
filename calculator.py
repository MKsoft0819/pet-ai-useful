import streamlit as st
from google import genai

# --- ページ設定（犬専用タイトル！） ---
st.set_page_config(
    page_title="AI Dog Meal Planner 🐶",
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- 魔法の隠し金庫（Secrets）からAPIキーを読み込む ---
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# --- ポップなカスタムCSS（犬らしい元気なオレンジ＆ブラウン系に微調整） ---
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
    background-color: #ff823a !important; /* ボタンを元気な犬カラーのオレンジに！ */
    color: white !important;
    border-radius: 30px !important;
    border: none !important;
    padding: 0.5rem 2rem !important;
    font-size: 1.2rem !important;
    font-weight: bold !important;
    width: 100%;
    box-shadow: 0 4px 15px rgba(255, 130, 58, 0.4);
}
/* トグルスイッチのONカラーもオレンジに変更 */
.stCheckbox > label > div[aria-checked="true"] > span {
    background-color: #ff823a !important;
}
[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# --- ヘッダーエリア ---
st.markdown('<p class="main-title">🐶 AI Dog Meal Planner</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b;">AIと一緒に、愛犬にぴったりのごはん量を見つけよう！</p>', unsafe_allow_html=True)

st.write("---")

# --- 1段目：基本情報 2列にスッキリ！（種類をなくした分、横幅に余裕ができました） ---
col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("体重 (kg) ⚖️", min_value=0.1, value=5.0, step=0.1)
with col2:
    activity_level = st.selectbox("活動量 🏃", ["低い（のんびり・お散歩少なめ）", "普通（標準的・毎日お散歩）", "高い（ドッグラン大好き・活動的）"])

# --- 2段目：年齢 と 体の状態 2列 ---
st.write("")
col3, col4 = st.columns(2)
with col3:
    age_group = st.selectbox(
        "年齢・ライフステージ 🎂", 
        ["生後4ヶ月未満（子犬・幼齢期） 🍼", "生後4ヶ月〜1歳まで（子犬・成長期） 🌱", "成犬（1歳〜） 🐕", "シニア（7歳〜） 🧓", "ハイシニア（11歳〜） 🌟"]
    )
with col4:
    pet_status = st.selectbox(
        "体の状態 🩺", 
        ["手術していない（未去勢・未避妊）", "手術している（去勢・避妊済み）", "妊娠前半（交配〜5週目頃） 🤰", "妊娠後半（5週目〜出産まで） 🔥🤰", "授乳中（子育て中！） 🍼✨"]
    )

# --- 3段目：ドッグフードのカロリー ---
st.write("")
food_calories = st.number_input(
    "ドッグフードのカロリー (100gあたり/kcal) 🍖", 
    min_value=100, max_value=600, value=350, step=5
)

# --- おやつ入力セクション ---
st.write("")
has_snacks = st.checkbox("今日はおやつをあげる？ 🦴")

snack_cal_per_100g = 0
snack_grams = 0

if has_snacks:
    st.info("おやつのパッケージの数字と、あげる量を入力してね！")
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

# --- メモエリア ---
st.write("")
memo = st.text_input("AI獣医へのメッセージ 💬", placeholder="例：最近少し太り気味、トイプードルです、など")

# --- 計算・AIアドバイス実行ボタン ---
st.write("")
if st.button("AIに相談して計算する ✨"):
    # AIへの依頼文（犬専用の栄養学をベースにするよう指示！）
    prompt = f"""
あなたは親切な「犬専門の獣医」です。以下の情報を元に、愛犬の1日あたりの推定給餌量(グラム)を計算してください。

情報：
- 対象: 犬
- 体重: {weight}kg
- 活動量: {activity_level}
- 年齢・ライフステージ: {age_group}
- 体の状態: {pet_status}
- ドッグフードのカロリー: 100gあたり {food_calories} kcal
- 今日あげるおやつのカロリー: 100gあたり {snack_cal_per_100g} kcal
- 今日あげるおやつの量: {snack_grams} g
- 飼い主からのメモ: {memo}

計算のステップ：
1. 犬の犬種や体重を考慮し、犬の安静時エネルギー要求量（RER = 70 × 体重^0.75）をベースに、ライフステージや状態を掛け合わせた1日の総必要エネルギー（DER）を算出してください。
2. 総必要エネルギーからおやつ分のカロリー（{snack_grams}g × {snack_cal_per_100g}kcal ÷ 100）を差し引いてください。
3. 残りのエネルギーをドッグフード（100gあたり{food_calories}kcal）で割って、1日の正確なグラム数を算出してください。

回答の構成：
1. おやつ分を差し引いた、1日のドッグフードの量（グラム）を大きく提示。
2. 計算の内訳（愛犬の総必要カロリー、おやつ分のカロリー、残りのごはんの量）を分かりやすく解説。
3. もしおやつのカロリーが1日の総カロリーの10%を超えていたら、犬の健康（肥満防止）のために優しく注意喚起してください。
4. 愛犬と飼い主さんがハッピーになれるような、温かくポップな一言アドバイス。
"""
    
    with st.spinner("ワンちゃんのためにAIが猛スピードで計算中... 🧠🐕⚖️"):
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
st.caption("※この計算は目安です。愛犬の体調に合わせて調整してあげてくださいね。 ...ワンッ！✨")