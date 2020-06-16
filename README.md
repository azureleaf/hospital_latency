# 病院自動予約君

- 某病院のオンライン予約を自動で行うスクリプトです。
- また、その病院の混雑状況をリアルタイムに自動取得します。これにより自分の診察がいつ頃になるか見当をつけやすくなります。

## ToC

- [病院自動予約君](#病院自動予約君)
  - [ToC](#toc)
  - [Purpose](#purpose)
    - [予約の早起きするのが大変なのを解決したい](#予約の早起きするのが大変なのを解決したい)
    - [自分の診察がいつ頃になるのか予測したい](#自分の診察がいつ頃になるのか予測したい)
  - [Usage](#usage)
    - [Requirements](#requirements)
    - [A. Automatic Reservation](#a-automatic-reservation)
    - [B. Automatic Retrieval](#b-automatic-retrieval)
    - [C. Analysis on Exam Speed](#c-analysis-on-exam-speed)
  - [Retrieval Result](#retrieval-result)
  - [Todos](#todos)

## Purpose

### 予約の早起きするのが大変なのを解決したい

- 私のかかりつけ病院を受診するためには、診察前にオンライン予約が必要です。
- この予約は当日の早朝にならないと受け付けてくれず、また先着順で締め切られてしまいます。
- このため、<u>患者はみな早朝に早起きしてパソコンの前で待ち構える必要があるのです。</u>大変です。
- この予約動作を自動でやってくれれば、朝もぐっすり眠れます！

### 自分の診察がいつ頃になるのか予測したい

- オンライン予約では診察番号（自分が何番目に診察されるのか）は取得できますが、それが何時頃になるかはわかりません。
- 現在診察を受けている患者の診察番号は、リアルタイムで病院ウェブサイトに表示されます。
- しかし、<u>病院のウェブサイトに何十回も自分で確認しにいくのは面倒です。</u>
- このプログラムは現在の診察番号を自動取得し、画面に表示し、またファイルに記録します。
- プログラムを何日か常駐させれば、その記録から診察の平均速度を割り出せます。これにより何時頃家を出るべきか推測しやすくなります。

## Usage

### Requirements

1. Install `python3` and `pipenv`
1. `pipenv shell`
2. `pipenv install`

### A. Automatic Reservation

1. 自分のOS環境に合わせたSelenium driverを [internet](https://chromedriver.chromium.org/downloads) からダウンロードする。
2. `vim ~/.bashrc`
    ```sh
    export SELENIUM_DRIVER_PATH="PATH_TO_THE_SELENIUM_DRIVER"   

    export PATIENT_INFO="{
        \"url_reserve\": \"https://foobarhospital.co.jp/reserve\",
        \"url_retrieve\": \"https://foobarhospital.co.jp/retrieve\",
        \"birth_era\": \"平成\", 
        \"birth_year\": \"1\",
        \"birth_month\": \"1\",
        \"birth_day\": \"1\",
        \"mail\": \"johndoe@gmail.com\",
        \"id\": \"11111\"
    }"
    ```
3. `source .bashrc`
5. `python3 auto_reserve.py`

### B. Automatic Retrieval

1. Set params in the `retrieve.py`
   - retrieval_cycle: 診察番号取得の実行間隔（分）
3. `python retrieve.py`。

### C. Analysis on Exam Speed

1. Set params in the `analyze.py`
   - my_reception_num: 自分の診察番号
   - now_reception_num: 現在の診察番号
   - now_time: 現在時刻（HHMM）
3. `python analyze.py`

## Retrieval Result 

- 時間帯別の平均診察人数は以下の通りでした。
- 夜になると処理速度が激増するのは、「診察番号をとったけどやっぱり行かないことにした人」が増えるためです。

![時間帯別の平均速度](average_throughput.png)


## Todos

- CUIだとインターフェースが使いにくすぎて非実用的なので、LINEボットやFlaskで展開すべき
- `analyze.py`の内容が非科学的。偏差なども描画すべき。時刻を丸めるところが統計学的に雑すぎるので、離散観測データを連続値に補間した上で、平均を計算すべき？
- 曜日変動を考慮できればおもしろい...が、時系列解析はデータの性質上、難しい？観測値が小さすぎる上に、各患者の一人あたり受診時間は完全にランダムなので前後に相関がない