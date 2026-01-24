# index.html 程式碼教學說明

給完全不會程式的新手看的超詳細解說！

---

## 網頁的三大組成

一個網頁由三種語言組成：

| 語言 | 負責什麼 | 比喻 |
|------|----------|------|
| **HTML** | 網頁的內容和結構 | 房子的骨架 |
| **CSS** | 網頁的外觀和樣式 | 房子的裝潢 |
| **JavaScript** | 網頁的互動功能 | 房子的電器設備 |

---

# 第一部分：HTML 結構

## 1. 文件開頭宣告

```html
<!DOCTYPE html>
```
- **DOCTYPE** = Document Type（文件類型）
- 告訴瀏覽器：「這是一個 HTML5 網頁」

---

```html
<html lang="zh-TW">
```
- **html** = 網頁的最外層容器
- **lang** = language（語言）
- **zh-TW** = 繁體中文（台灣）

---

## 2. head 區塊（網頁的設定資訊）

```html
<head>
    ...
</head>
```
- **head** = 頭部，放「看不見」的設定資訊
- 使用者不會直接看到這裡的內容

---

```html
<meta charset="UTF-8">
```
- **meta** = metadata（元資料），網頁的設定資訊
- **charset** = character set（字元集）
- **UTF-8** = 一種編碼方式，支援中文、日文、表情符號等

---

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
- **viewport** = 可視區域（螢幕顯示範圍）
- **width=device-width** = 寬度等於裝置寬度
- **initial-scale=1.0** = 初始縮放比例為 1（不放大不縮小）
- 這行讓網頁在手機上也能正常顯示

---

```html
<title>台北天氣查詢系統</title>
```
- **title** = 標題
- 會顯示在瀏覽器的分頁標籤上

---

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```
- **script** = 腳本（程式碼）
- **src** = source（來源）
- 引入 Chart.js 這個畫圖表的工具
- **cdn** = Content Delivery Network（內容傳遞網路），別人的伺服器

---

## 3. body 區塊（網頁的可見內容）

```html
<body>
    ...
</body>
```
- **body** = 身體，放「看得見」的網頁內容

---

### 常見的 HTML 標籤

| 標籤 | 英文全名 | 意思 | 用途 |
|------|----------|------|------|
| `<div>` | division | 區塊 | 把內容分組 |
| `<h1>` | heading 1 | 標題1 | 最大的標題 |
| `<h2>` | heading 2 | 標題2 | 第二大標題 |
| `<p>` | paragraph | 段落 | 一段文字 |
| `<button>` | button | 按鈕 | 可點擊的按鈕 |
| `<input>` | input | 輸入 | 讓使用者輸入資料 |
| `<label>` | label | 標籤 | 說明輸入欄位的用途 |
| `<table>` | table | 表格 | 顯示表格資料 |
| `<tr>` | table row | 表格列 | 表格的一橫排 |
| `<th>` | table header | 表頭 | 表格的標題欄 |
| `<td>` | table data | 表格資料 | 表格的一格 |
| `<ul>` | unordered list | 無序列表 | 項目符號清單 |
| `<li>` | list item | 列表項目 | 清單中的一項 |
| `<aside>` | aside | 側邊 | 側邊欄 |
| `<main>` | main | 主要 | 主要內容區 |
| `<canvas>` | canvas | 畫布 | 用來畫圖表 |

---

### HTML 屬性（寫在標籤裡面的設定）

```html
<div class="container" id="myDiv">
```

| 屬性 | 英文全名 | 意思 | 用途 |
|------|----------|------|------|
| `class` | class | 類別 | 給元素分類，CSS 用 |
| `id` | identifier | 識別碼 | 給元素取名，唯一的 |
| `style` | style | 樣式 | 直接寫 CSS |
| `onclick` | on click | 當點擊時 | 點擊時執行某功能 |
| `type` | type | 類型 | 指定輸入類型 |
| `value` | value | 值 | 欄位的值 |

---

# 第二部分：CSS 樣式

## CSS 基本語法

```css
.sidebar {
    width: 300px;
    background: white;
    padding: 20px;
}
```

- `.sidebar` = 選擇器（selector），選擇 class="sidebar" 的元素
- `{ }` = 大括號裡面放樣式設定
- `width: 300px;` = 寬度 300 像素
- 每行結尾要加 `;` 分號

---

## 選擇器類型

| 寫法 | 意思 | 範例 |
|------|------|------|
| `.名稱` | 選擇 class | `.sidebar` 選擇 class="sidebar" |
| `#名稱` | 選擇 id | `#loading` 選擇 id="loading" |
| `標籤` | 選擇所有該標籤 | `body` 選擇所有 body |
| `*` | 選擇所有元素 | `*` 選擇全部 |

---

## 常用 CSS 屬性

### 尺寸相關

| 屬性 | 英文 | 意思 | 範例 |
|------|------|------|------|
| `width` | width | 寬度 | `width: 300px` |
| `height` | height | 高度 | `height: 400px` |
| `min-width` | minimum width | 最小寬度 | `min-width: 120px` |
| `min-height` | minimum height | 最小高度 | `min-height: 100vh` |

**單位說明：**
- `px` = pixel（像素），固定大小
- `%` = 百分比，相對於父元素
- `vh` = viewport height（視窗高度的百分比）
- `vw` = viewport width（視窗寬度的百分比）

---

### 顏色相關

| 屬性 | 英文 | 意思 | 範例 |
|------|------|------|------|
| `color` | color | 文字顏色 | `color: white` |
| `background` | background | 背景 | `background: #f0f0f0` |
| `border` | border | 邊框 | `border: 2px solid #ccc` |

**顏色寫法：**
- `white`、`red`、`blue` = 顏色英文名稱
- `#FF6B6B` = 十六進位色碼（# 後面 6 個字元）
- `rgba(255, 255, 255, 0.95)` = RGB + 透明度
  - r = red（紅）0-255
  - g = green（綠）0-255
  - b = blue（藍）0-255
  - a = alpha（透明度）0-1

---

### 間距相關

| 屬性 | 英文 | 意思 | 說明 |
|------|------|------|------|
| `margin` | margin | 外距 | 元素「外面」的空白 |
| `padding` | padding | 內距 | 元素「裡面」的空白 |

```
┌─────────────────────────┐
│       margin（外距）      │
│  ┌───────────────────┐  │
│  │   padding（內距）   │  │
│  │  ┌─────────────┐  │  │
│  │  │   內容      │  │  │
│  │  └─────────────┘  │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

---

### 文字相關

| 屬性 | 英文 | 意思 | 範例 |
|------|------|------|------|
| `font-size` | font size | 字體大小 | `font-size: 16px` |
| `font-weight` | font weight | 字體粗細 | `font-weight: 600`（600=粗體） |
| `font-family` | font family | 字體家族 | `font-family: 'Microsoft JhengHei'` |
| `text-align` | text align | 文字對齊 | `text-align: center`（置中） |
| `line-height` | line height | 行高 | `line-height: 1.8` |

---

### 排版相關

| 屬性 | 英文 | 意思 | 範例 |
|------|------|------|------|
| `display` | display | 顯示方式 | `display: flex` |
| `flex` | flexible | 彈性 | 彈性排版 |
| `position` | position | 定位 | `position: relative` |

**display 常見值：**
- `block` = 區塊（佔滿一整行）
- `inline` = 行內（只佔需要的寬度）
- `flex` = 彈性排版（現代常用）
- `none` = 不顯示（隱藏）

---

### 視覺效果

| 屬性 | 英文 | 意思 | 範例 |
|------|------|------|------|
| `border-radius` | border radius | 邊框圓角 | `border-radius: 10px` |
| `box-shadow` | box shadow | 盒子陰影 | `box-shadow: 0 4px 15px rgba(0,0,0,0.1)` |
| `opacity` | opacity | 透明度 | `opacity: 0.5`（50% 透明） |
| `cursor` | cursor | 游標 | `cursor: pointer`（手指圖示） |
| `transition` | transition | 過渡動畫 | `transition: all 0.3s` |

---

### 特殊選擇器

```css
.query-btn:hover {
    transform: translateY(-2px);
}
```

| 選擇器 | 意思 | 用途 |
|--------|------|------|
| `:hover` | 滑鼠懸停時 | 滑鼠移上去的效果 |
| `:focus` | 聚焦時 | 點擊輸入框時的效果 |
| `:active` | 點擊時 | 按下按鈕時的效果 |
| `:disabled` | 禁用時 | 按鈕不能按時的效果 |

---

### 響應式設計

```css
@media (max-width: 768px) {
    .sidebar {
        width: 100%;
    }
}
```

- `@media` = 媒體查詢
- `max-width: 768px` = 當螢幕寬度小於 768px 時
- 用於手機版網頁的樣式調整

---

# 第三部分：JavaScript 功能

## 基本概念

### 變數宣告

```javascript
let weatherData = null;
const today = new Date();
```

| 關鍵字 | 意思 | 用途 |
|--------|------|------|
| `let` | 讓 | 宣告可以改變的變數 |
| `const` | constant（常數） | 宣告不能改變的變數 |
| `null` | null（空） | 表示「沒有值」 |

---

### 函式（Function）

```javascript
function initDates() {
    // 程式碼...
}
```

- `function` = 函式（功能）
- `initDates` = 函式名稱（initialize dates = 初始化日期）
- `()` = 參數，可以傳資料進去
- `{ }` = 函式的內容

---

### 常見單字對照

| 英文 | 意思 | 說明 |
|------|------|------|
| `init` | initialize | 初始化 |
| `get` | get | 取得 |
| `set` | set | 設定 |
| `fetch` | fetch | 抓取（資料） |
| `data` | data | 資料 |
| `response` | response | 回應 |
| `error` | error | 錯誤 |
| `async` | asynchronous | 非同步（不用等待） |
| `await` | await | 等待 |
| `try` | try | 嘗試 |
| `catch` | catch | 捕捉（錯誤） |
| `finally` | finally | 最後（不管成功失敗都執行） |

---

### DOM 操作

```javascript
document.getElementById('startDate')
```

- `document` = 整個網頁文件
- `getElementById` = get element by id（用 id 取得元素）
- 回傳 id="startDate" 的那個元素

---

```javascript
document.getElementById('loading').classList.add('active');
```

- `classList` = class 清單
- `add('active')` = 加入 'active' 這個 class
- `remove('active')` = 移除 'active' 這個 class
- `toggle('active')` = 切換（有就移除，沒有就加入）

---

### 事件監聽

```javascript
document.getElementById('startDate').addEventListener('change', function() {
    // 當日期改變時執行...
});
```

- `addEventListener` = add event listener（加入事件監聽器）
- `'change'` = 當值改變時
- `function() { }` = 要執行的動作

**常見事件：**
| 事件 | 意思 |
|------|------|
| `click` | 點擊 |
| `change` | 值改變 |
| `submit` | 表單送出 |
| `load` | 載入完成 |
| `keydown` | 按下鍵盤 |

---

### API 呼叫

```javascript
async function fetchWeatherData() {
    const response = await fetch('/api/weather?start_date=...');
    const data = await response.json();
}
```

- `async` = 非同步函式
- `await` = 等待結果
- `fetch()` = 發送網路請求
- `response.json()` = 把回應轉成 JSON 格式

---

### 陣列方法

```javascript
weatherData.map(d => d.date)
```

- `map` = 映射，把每個元素轉換成新的值
- `d => d.date` = 箭頭函式，把 d 轉成 d.date
- 結果：取出所有的日期

```javascript
weatherData.forEach(day => {
    // 對每個 day 做某件事
});
```

- `forEach` = for each（對每一個）
- 對陣列的每個元素執行某動作

---

### 條件判斷

```javascript
if (response.ok && data.success) {
    // 成功時執行
} else {
    // 失敗時執行
}
```

- `if` = 如果
- `else` = 否則
- `&&` = AND（而且）
- `||` = OR（或者）
- `!` = NOT（不是）

---

### 樣板字串

```javascript
`成功獲取 ${startDate} 至 ${endDate} 的資料`
```

- 用反引號 \` \`（不是單引號）
- `${變數}` = 插入變數的值

---

## 程式流程說明

### 1. 網頁載入時

```javascript
document.addEventListener('DOMContentLoaded', initDates);
```

當網頁載入完成（DOMContentLoaded），執行 `initDates()` 函式

### 2. 初始化日期

`initDates()` 做了什麼：
1. 取得今天日期
2. 計算 7 天後的日期
3. 填入開始日期和結束日期
4. 更新顯示的日期範圍

### 3. 使用者點擊查詢

`fetchWeatherData()` 做了什麼：
1. 顯示「載入中」
2. 向後端 API 發送請求
3. 等待回應
4. 成功 → 顯示資料
5. 失敗 → 顯示錯誤訊息
6. 隱藏「載入中」

### 4. 顯示結果

`displayResults()` 做了什麼：
1. 畫溫度圖表
2. 填入表格資料
3. 建立日期按鈕

---

## 常見符號說明

| 符號 | 名稱 | 用途 |
|------|------|------|
| `{ }` | 大括號 | 程式區塊、物件 |
| `[ ]` | 中括號 | 陣列 |
| `( )` | 小括號 | 函式參數、群組 |
| `;` | 分號 | 語句結束 |
| `:` | 冒號 | 鍵值對分隔 |
| `,` | 逗號 | 項目分隔 |
| `.` | 點 | 存取屬性或方法 |
| `=>` | 箭頭 | 箭頭函式 |
| `===` | 三等號 | 嚴格相等比較 |
| `!==` | 不等於 | 嚴格不相等比較 |
| `//` | 雙斜線 | 單行註解 |
| `/* */` | 斜線星號 | 多行註解 |

---

## 總結

這個網頁的運作流程：

```
1. 瀏覽器載入 HTML
      ↓
2. 載入 CSS 樣式
      ↓
3. 載入 JavaScript
      ↓
4. 執行 initDates() 初始化
      ↓
5. 使用者選擇日期、點擊查詢
      ↓
6. JavaScript 發送請求到後端
      ↓
7. 後端回傳天氣資料
      ↓
8. JavaScript 處理資料、更新畫面
      ↓
9. 使用者看到結果
```

恭喜你看完了！有問題隨時問 😊
