# 光點驅動附加元件

「光點」是[宇崝](http://www.u-tran.com/)公司販售的一款點字顯示器。宇崝公司亦提供對應之 NVDA 驅動附加元件，然而該附加元件目前可取得之最新版本 1.03 已無法在 NVDA 2019.3 或以上版本運作。因為宇崝公司並未再提供該附加元件之新版以相容 NVDA 2019.3 或以上版本，所以 [Bo-Cheng Jhan &lt;school510587@yahoo.com.tw&gt;](mailto:school510587@yahoo.com.tw) 將自行改進之版本放在此儲存庫讓使用者們免費下載。

本附加元件的取得、散步與修改皆受 GPL 之條文規範，詳情請見 COPYING.txt。

### 安裝

安裝此附加元件之前，請先確定您已經準備好[原廠的驅動程式](https://class.kh.edu.tw/sites/19061/bulletin_file/478/MetecBD.zip)。啟動此檔案後請依照 NVDA 之指示進行安裝即可。如果仍然無法抓取光點裝置，可能是 Windows 10 沒有正確設定光點與所對應的驅動程式，請參考[此處](https://class.kh.edu.tw/19061/bulletin/msg_view/151)說明來修正該設定。

### 設定 NVDA 連接到光點

1. 進入「偏好設定」的「點字」項目
2. 開啟「選擇點顯器」視窗
3. 選擇「U-Tran 光點點字顯示器」
4. 按「確定」離開視窗，進行其他點字方面的設定
5. 按「套用」或「確定」使其生效

◎可以用 Ctrl + NVDA + A 快速開啟「選擇點顯器」視窗。

### 錯誤回報

NVDA 自 2019.3 版起會檢查附加元件最後測試之 NVDA 版本，最後通過測試之 NVDA 版本若未達使用者之 NVDA 版本即停用附加元件。本附加元件版號的最後兩節即為通過測試之最後 NVDA 版本，當發現 NVDA 更新導致本附加元件無法作用時，請至[這裡](https://github.com/school510587/MetecBD-driver/releases)看看是否有符合您需要的版本。假如沒有，請登入 GitHub 並在該儲存庫的 Issues 當中寫出您的需求，或者將您的需求發表在 [NVDA 台灣郵遞論壇](https://groups.io/g/nvda-tw)。如果發現本附加元件運作有錯誤發生，也可透過上述管道反映。
