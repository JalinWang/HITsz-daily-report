# HITsz Daily Report

基于 GitHub Actions 的「HITsz 疫情系统」<sup>[访问入口](http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/yqxx)</sup> 定时自动上报脚本，开箱即用。

感谢 [@JellyBeanXiewh](https://github.com/JellyBeanXiewh/) 提供原始脚本和 idea。  
感谢 [@bugstop](https://github.com/bugstop/) 对脚本进行重构并新增 Easy Connect 校内代理访问。

## 使用方法

1. `Fork` 仓库
2. 设置仓库的 Actions Secrets <sup>[如何设置？](./how-to-enable-actions/#添加-Secrets)</sup>  
   添加用户名 `USERNAME` 和密码 `PASSWORD` ，以及可选的 `GRADUATING` 和 `API_KEY`
   | Name | Value |
   | :---: | :---: |
   | USERNAME | HITsz 统一身份认证用户名（学号） |
   | PASSWORD | HITsz 统一身份认证密码 |
   | GRADUATING | 毕业班请设为 `1` ，非毕业班学生请留空（不设置） |
   | API_KEY | 微信推送的 `sckey` <sup>[如何申请？](http://sc.ftqq.com/?c=wechat&a=bind)</sup>，不需要请留空（不设置） |
3. 开启 GitHub Actions <sup>[如何开启？](./how-to-enable-actions/#启用-Actions)</sup>
4. 每天早上 7:00 <sup>23:00 UTC</sup> 定时自动运行  
   如果填写 `API_KEY` ，即可在微信上收到运行结果推送（由 [Server 酱](http://sc.ftqq.com/)提供）  
   或者你可以打开 GitHub Actions 执行的全局邮件通知 <sup>[如何开启？](./how-to-enable-actions/#设置邮件提醒)</sup>，包括成功或失败信息

## Change Log

参阅 [Releases](https://github.com/JalinWang/HITsz-daily-report/releases) 列表。
