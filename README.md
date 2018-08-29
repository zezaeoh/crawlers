# crawlers

## depndency
1. scrapy
2. selenium (phantom.js)
3. redis
4. rq

## log
* unix계열 /var/log/ 아래에 생성 **로그정보가 없을시 6시간정도의 데이터를 크롤링**

## Item Pipeline
* RQPipeline : rq서버로 crawling한 item을 전달 (rq서버에서 데이터 저장 담당)
* JsonPipeline : 각 크롤러의 프로젝트 폴더 아래에 crawling한 data를 json 파일로 저장 (test용)

## Spitz_Crawler
### spider
* **spitz_crawler** : 오늘의 유머 크롤링
### how to use
```
  $ scrapy crawl spitz_crawler
```
## Beagle_Crawler
### spider
* **beagle_crawler_bbs** : 뽐뿌 자유게시판 크롤링
* **beagle_crawler_etc_info** : 뽐뿌 생활정보 게시판 크롤링
* **beagle_crawler_app_info** : 뽐뿌 앱정보 게시판 크롤링
* **beagle_crawler_ppomppu** : 뽐뿌 뽐뿌게시판 크롤링
### how to use
```
  $ scrapy crawl beagle_crawler_bbs
  $ scrapy crawl beagle_crawler_etc_info
  $ scrapy crawl beagle_crawler_app_info
  $ scrapy crawl beagle_crawler_ppomppu
```
## Poodle_Crawler
### spider
* **poodle_crawler** : dcinside 크롤링
### how to use
```
  $ scrapy crawl poodle_crawler -a gall_id=<갤러리 id>
```
## Dachshund_Crawler
### spider
* **dachshund_crawler** : 네이버카페 레몬테라스 크롤링
### how to use
```
  $ scrapy crawl dachshund_crawler
```
## Pointer_Crawler
### spider
* **pointer_crawler** : 클리앙 크롤링
### how to use
```
  $ scrapy crawl pointer_crawler
```
* _현재 테스트중이므로 Json파일로만 저장됩니다._

## Retriever_Crawler
### spider
* **retriever_crawler** : 루리웹 크롤링
### how to use
```
  $ scrapy crawl retriever_crawler -a board_id=<게시판 id>
```
* _현재 테스트중이므로 Json파일로만 저장됩니다._

## Processing_Scheduler
### spider
* **processing_start** : 데이터 프로세싱을 위한 스케쥴링 명령 전달
### how to use
```
  $ scrapy crawl process_start -a cycle=<사이클 넘버> -a is_first=<True or False>
```
