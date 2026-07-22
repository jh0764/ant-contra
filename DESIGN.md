---
name: 개미반대로 (Ant-Contra)
description: 보조지표와 커뮤니티 여론을 실시간 결합한 친근하고 따뜻한 역발상 투자 대시보드
colors:
  primary: "#FF7A2F"
  neutral-bg: "#EEF0F3"
  surface: "#FFFFFF"
  border: "#DDE1E6"
  text-main: "#1A1D29"
  text-sub: "#6B7280"
  status-green-bg: "#DCFCE7"
  status-green-border: "#16A34A"
  status-yellow-bg: "#FEF3C7"
  status-yellow-border: "#CA8A04"
  status-red-bg: "#FEE2E2"
  status-red-border: "#DC2626"
  price-up: "#f04452"
  price-down: "#3182f6"
typography:
  display:
    fontFamily: "Pretendard, -apple-system, sans-serif"
    fontSize: "32px"
    fontWeight: 800
    lineHeight: 1.2
  headline:
    fontFamily: "Pretendard, -apple-system, sans-serif"
    fontSize: "24px"
    fontWeight: 800
    lineHeight: 1.3
  title:
    fontFamily: "Pretendard, -apple-system, sans-serif"
    fontSize: "19px"
    fontWeight: 800
    lineHeight: 1.4
  body:
    fontFamily: "Pretendard, -apple-system, sans-serif"
    fontSize: "13.5px"
    fontWeight: 600
    lineHeight: 1.5
  label:
    fontFamily: "Pretendard, -apple-system, sans-serif"
    fontSize: "12.5px"
    fontWeight: 700
    lineHeight: 1
rounded:
  sm: "5px"
  md: "8px"
  lg: "10px"
  xl: "12px"
  xxl: "14px"
  full: "999px"
spacing:
  sm: "5px"
  md: "10px"
  lg: "12px"
  xl: "14px"
  xxl: "16px"
components:
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "12px 14px"
  button-tab-active:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: "6px 14px"
  badge-pill:
    rounded: "{rounded.full}"
    padding: "7px 18px"
---

# Design System: 개미반대로 (Ant-Contra)

## 1. Overview

**Creative North Star: "The Rational Shelter" (이성적 대피소)**

개미반대로(Ant-Contra)의 디자인 시스템은 복잡하고 극단적인 감정이 오가는 주식 시장에서 개미 투자자들이 이성적인 판단을 내릴 수 있도록 돕는 '차분하고 안락한 대피소'를 지향합니다. 커뮤니티 게시판의 혼란스럽고 왜곡된 심리를 걷어내고, 정돈된 레이아웃과 따뜻한 톤, 그리고 친근한 인터랙션을 통해 투자자가 스트레스와 불안감 없이 시장을 객관적으로 응시하도록 돕습니다.

이 시스템은 정교하지만 위압감을 주는 전문 트레이더용 단말기의 형태나, 지나치게 화려한 색상이 깜빡이는 복잡한 대시보드를 지양합니다. 그 대신, 넓고 여유로운 패딩과 눈이 편안한 미색 배경, 직관적으로 둥글게 다듬어진 카드를 통해 사용자에게 정서적이고 시각적인 차분함을 안겨줍니다.

**Key Characteristics:**
- 따뜻하고 정돈된 미색 계열의 라이트모드 테마
- 정서적 안정감을 제공하는 둥글고 여유로운 폼팩터
- 음영을 배제하고 경계선(border)과 면 분할로만 깊이를 표현하는 플랫 레이아웃
- 복잡한 수식을 친근하고 쉽게 풀어쓴 다정한 어조의 한국어 카피

## 2. Colors

Ant-Contra의 색상은 편안함을 제공하는 미색 계열의 뉴트럴 톤과, 사용자의 눈길을 자연스럽게 끄는 따뜻한 포인트 컬러, 그리고 명확한 상태 전달을 돕는 신호등 시스템으로 구성됩니다.

### Primary
- **Sunset Orange** (`#FF7A2F`): 주로 사용자가 활성화한 필터, 선택된 탭, 핵심 액션 버튼 등에 쓰이는 주색상입니다. 차분한 배경 위에서 따뜻한 활력과 명확한 초점을 제공합니다.

### Neutral
- **Slate Gray Base** (`#EEF0F3`): 전체 대시보드의 백그라운드 색상입니다. 순백색의 차가운 눈부심을 방지하고 따뜻하고 편안한 인상을 주는 미색 톤입니다.
- **Pure White Surface** (`#FFFFFF`): 각 위젯 및 카드 영역의 배경입니다. 백그라운드와 시각적으로 구분되어 정보를 영역화합니다.
- **Cool Gray Border** (`#DDE1E6`): 카드의 외곽선이나 구분선에 사용되는 기본 보더 색상입니다. 정보를 선명하게 잡아주면서도 화면이 지저분해 보이지 않게 설계되었습니다.
- **Ink Black Text** (`#1A1D29`): 대시보드 내의 핵심 타이틀과 중요 텍스트에 쓰이는 진한 먹색입니다.
- **Muted Stone Text** (`#6B7280`): 설명, 캡션, 보조 텍스트에 쓰여 텍스트 위계를 다듬는 차분한 회색입니다.

### Status & Market Signals
- **East Asian Price Tones**:
  - **Bullish Red** (`#f04452`): 동아시아 주식 시장 관습에 맞춘 가격 상승 색상입니다.
  - **Bearish Blue** (`#3182f6`): 동아시아 주식 시장 관습에 맞춘 가격 하락 색상입니다.
- **Indicator Status Tones**:
  - **Fear-Scream Green** (`#16A34A` bg `#DCFCE7`): 비명 지수가 감지되어 역발상 매수 타이밍으로 간주되는 긍정적 시그널 색상입니다.
  - **Neutral Yellow** (`#CA8A04` bg `#FEF3C7`): 가격과 여론이 균형을 이루고 있는 중립 상태의 색상입니다.
  - **Overheated Red** (`#DC2626` bg `#FEE2E2`): 개미들의 군중 심리가 과열되어 있는 위험 상태의 색상입니다.

**The Sunset Constraint Rule.** Sunset Orange 주색상은 화면 내에서 반드시 5% 이하의 비중으로만 사용되어야 합니다. 포인트 컬러의 희소성이 유지될 때 비로소 시선이 올바르게 고정되며 브랜드의 품격이 유지됩니다.

## 3. Typography

**Display Font:** `Pretendard` (fallback `-apple-system, sans-serif`)
**Body Font:** `Pretendard` (fallback `-apple-system, sans-serif`)

**Character:** 고도로 가독성이 확보된 현대적인 지오메트릭 폰트 Pretendard를 일관되게 사용합니다. 부드럽지만 선명한 웨이트 구성을 채택하여, 사용자가 복잡한 수치 정보 앞에서도 쉽게 긴장하지 않고 텍스트를 정독할 수 있도록 세심하게 다듬어졌습니다.

### Hierarchy
- **Display** (800, `32px` / `56px`, 1.2): 랜딩 화면의 로고나 대형 이모지 배너 등에만 제한적으로 사용합니다.
- **Headline** (800, `24px`, 1.3): 대시보드 메인 페이지의 핵심 타이틀입니다.
- **Title** (800, `19px`, 1.4): 각 개별 카드의 제목과 서브 타이틀 영역에 적용됩니다.
- **Body** (600, `13.5px`, 1.5): 일반 본문 설명 및 데이터 라벨 텍스트입니다. 가독성을 고려하여 한 행의 최대 길이는 75ch로 엄격하게 제어합니다.
- **Label** (700, `12.5px`, 1.0): 캡슐 알약 형태의 탭 텍스트, 메타 정보 영역에 적용됩니다.

### Named Rules
**The High-Legibility Contrast Rule.** 텍스트는 배경색 대비 최소 4.5:1 이상의 명도비를 엄격하게 충족해야 합니다. 메타 텍스트나 서브 라벨조차 흐릿한 회색으로 표기하여 가독성을 해치는 우를 범하지 않습니다.

## 4. Elevation

Ant-Contra는 전반적으로 **Flat & Bordered** 입체 철학을 지지합니다. 복잡하고 화려한 드롭 섀도나 입체 광택 효과는 화면을 산만하게 만들고 정보 인지를 방해합니다. 따라서 그림자는 극히 제한된 사용자 조작 피드백(마우스 호버 등)에만 얇게 적용하며, 평소에는 정교하게 조율된 보더(`{colors.border}`)와 미색 표면(`{colors.surface}`) 간의 선명한 대비로 격조 높은 레이아웃을 전개합니다.

## 5. Components

모든 컴포넌트는 사용자의 심리적 허들을 낮추고 포근한 사용성을 제공하도록 넉넉한 여백과 둥근 반경을 지니고 있습니다.

### Cards
- **Shape:** Rounded-lg (`10px` radius) 또는 Rounded-xl (`12px` radius).
- **Structure:** 섀도 없이 선명한 1px의 실선 테두리(`{colors.border}`)와 솔리드 흰색 배경(`{colors.surface}`)으로 감싸여 정보의 영역을 단단하게 확보합니다.
- **Padding:** 12px에서 14px 사이의 넉넉한 이너 패딩을 제공하여 텍스트와 보조 지표가 산소 호흡 공간을 갖도록 합니다.

### Navigation & Tab Groups
- **Structure:** 둥글게 마감된 하나의 긴 캡슐 트랙(Rounded-xl, `{colors.border}`) 안에 알약 모양의 버튼(Rounded-md)이 올라갑니다.
- **Active State:** 선택된 알약은 배경이 흰색(`{colors.surface}`)으로 변경되고 글씨가 `{colors.primary}`로 바뀌며, 가벼운 1px의 섀도가 더해져 물리적인 스위치감을 부여합니다.
- **Inactive State:** 미선택 버튼은 투명 배경을 취하며, 어조가 다운된 `{colors.text-sub}`를 머금습니다.

### Choice Pills / Radios
- **Shape:** 완전한 캡슐 형태(Rounded-full, `999px` radius).
- **Active State:** 솔리드 `{colors.primary}` 바탕에 깔끔한 검정 글씨(`#1a1a1a`)로 렌더링되며, 클릭 시 자연스럽게 통통 튀며 확대(`scale(1.06)`)되는 베지에 애니메이션 트랜지션을 취합니다.
- **Inactive State:** `{colors.primary}` 색상의 반투명 테두리와 짙은 배경을 머금고 뒤편으로 물러납니다.

## 6. Do's and Don'ts

### Do's
- 복잡한 수치 정보를 볼 때는 언제나 사용자가 즉시 이해할 수 있는 한글 캡션을 상세하게 적어주십시오.
- 카드는 언제나 드롭 섀도를 배제하고 1px 두께의 플랫한 외곽선으로만 정보를 감싸주십시오.
- Sunset Orange 주색상은 오직 사용자의 핵심 인터랙션 지점에만 국한하여 5% 미만으로 활용해 주십시오.
- 동아시아 기준인 빨간색(상승)/파란색(하락) 시장 관습을 존중하되, 형태나 수치 라벨을 함께 제공하여 색약 투자자들을 배려해 주십시오.

### Don'ts
- 카드나 경고 알림 영역 측면에 임의로 두꺼운 세로선 강조 테두리(e.g., `border-left: 5px`)를 그리지 마십시오. 이는 시선 흐름을 저해하는 금지 패턴입니다.
- 계층 구조가 과도하게 중첩된 다층형 네스티드 카드 레이아웃을 작성하지 마십시오.
- 화면 크기가 줄어든다고 해서 타이포그래피의 최소 가독 크기를 무시하고 글자를 작게 줄이지 마십시오. 가독성에 우선순위를 두고 반응형 클램프 한계를 설정하십시오.
- 어떠한 정보 표시용 라벨 텍스트도 배경 대비 4.5:1 명도비 기준선 이하로 내려가지 않도록 유의하십시오.
