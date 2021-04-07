# HITsz Daily Report

基于 Github Actions 的定时 HITsz 疫情上报脚本，开箱即用。  
感谢 [@JellyBeanXiewh](https://github.com/JellyBeanXiewh/) 提供原始脚本和 idea。

### [疫情上报系统入口](http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/yqxx)

## 使用方法

1. `Fork` 仓库
2. 设置仓库的 Actions Secrets  
   添加用户名 `USERNAME` 和密码 `PASSWORD` ，以及可选的 `GRADUATING` 和 `API_KEY`
   | Name | Value |
   | :---: | :---: |
   | USERNAME | HITsz 统一身份认证用户名 （学号） |
   | PASSWORD | HITsz 统一身份认证密码 |
   | IS_GRAD | 是否毕业生班：是 `1` ，否 `0`|
   | API_KEY | Server 酱推送的 `sckey` <sup>[如何申请？](http://sc.ftqq.com/)</sup>（留空则不推送） |
3. 开启 Github Actions <sup>[如何开启？](./how-to-enable-actions)</sup>
4. 每天早上 7:00 <sup>23:00 UTC</sup> 定时自动运行  
   如果填写 `API_KEY` ，即可在微信上收到运行结果推送
