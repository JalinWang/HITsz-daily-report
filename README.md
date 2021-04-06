# HITsz-daily-report

基于 Github Action 的定时 HITsz 疫情上报脚本，开箱即用。  
感谢  [@JellyBeanXiewh](https://github.com/JellyBeanXiewh/) 提供原始脚本和 idea 。

[疫情上报系统入口](http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/yqxx)

## 使用方法
1. `fork` 仓库
2. 设置仓库的 Action Secret ，添加用户名 `username` 、密码 `password` 和可选的 `API_KEY`
   |  Name  |  Value  |
   | :----: | :-----: |
   | username | HITsz 统一身份认证用户名 （学号） |
   | password | HITsz 统一身份认证密码           |
   | API_KEY  | Server 酱推送的 sckey <sup>[如何申请？](http://sc.ftqq.com/)</sup> |
3. 开启 Action <sup>[如何开启？](./.github)</sup>
4. 每天早上 7:00 (UTC 23:00) 可自动定时运行，如果填写 `API_KEY` ，即可在微信上收到运行结果推送

