import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_naver_discussion(ticker_code):
    """
    네이버 종목 토론방에서 최신 글 제목 20개를 긁어오는 함수
    """
    # 네이버 종토방 모바일 주소 (모바일 주소가 긁어오기 훨씬 깔끔합니다)
    url = f"https://m.stock.naver.com/domestic/stock/{ticker_code}/discussion"
    
    # 봇(Bot)으로 오해받지 않기 위해 브라우저인 척 위장하는 헤더 정보
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 페이지 요청 및 파싱
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # ⭐️ 네이버 종토방의 글 제목들이 담긴 태그 찾기
    # (네이버 사이트 구조 변경에 따라 태그명은 달라질 수 있습니다)
    title_tags = soup.select(".DiscussionAndNewsListItem_title__xxxxxxxx") # 임시 태그명
    
    # 만약 위 태그로 안 긁힐 경우를 대비한 대체 태그 샘플 추출
    titles = []
    for tag in soup.find_all("strong"):
        title_text = tag.get_text().strip()
        if title_text and len(title_text) > 2: # 너무 짧은 글자 제외
            titles.append(title_text)
            
    # 최신 글 10개만 솎아내기
    return titles[:10]

# 🔥 코드가 잘 돌아가는지 단독 테스트해보는 공간
if __name__ == "__main__":
    print("🚀 네이버 종토방 크롤러 테스트 시작...")
    
    # 삼성전자 종목 코드: 005930
    samsung_titles = get_naver_discussion("005930")
    
    print("\n💬 [삼성전자 종토방 최신 글 제목 TOP 10]")
    print("-" * 50)
    for i, title in enumerate(samsung_titles, 1):
        print(f"{i}위: {title}")
    print("-" * 50)