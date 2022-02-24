# HITsz Daily Report

基于 GitHub Actions 的「HITsz 疫情系统」<sup>[访问入口](https://student.hitsz.edu.cn/xg_mobile/loginChange)</sup> 定时自动上报脚本，开箱即用（适用于本硕）。

感谢 [@JellyBeanXiewh](https://github.com/JellyBeanXiewh/) 提供原始脚本和 idea。  
感谢 [@bugstop](https://github.com/bugstop/) 对脚本进行重构并新增 Easy Connect 校内代理访问。
感谢 [@chh13502](https://github.com/chh13502) 适配新学工系统。

## 免责声明

本脚本为减轻导员和负责人/班长通知成本而诞生，作者不对任何因个人瞒报而破坏疫情防治工作的行为负责！

##### 如果有发热状况，请及时私信通知导员！！！！
#### 如果有发热状况，请及时私信通知导员！！！！
### 如果有发热状况，请及时私信通知导员！！！！

## 使用方法

1. `Fork` 仓库
2. 设置仓库的 Actions Secrets <sup>[如何设置？](./how-to-enable-actions/#添加-Secrets)</sup>  
   添加用户名 `USERNAME` 和密码 `PASSWORD` ，以及可选的 `GRADUATING` 和 `API_KEY`
   | Name | Value |
   | :---: | :---: |
   | USERNAME | HITsz 统一身份认证用户名（学号） |
   | PASSWORD | HITsz 统一身份认证密码 |
   | API_KEY | 微信推送的 `sckey` <sup>[如何申请？](http://sc.ftqq.com/?c=wechat&a=bind)</sup>，不需要请留空（不设置） |
3. 开启 GitHub Actions <sup>[如何开启？](./how-to-enable-actions/#启用-Actions)</sup>
4. 每天早上 7:00 <sup>23:00 UTC</sup> 定时自动运行  
   如果填写 `API_KEY` ，即可在微信上收到运行结果推送（由 [Server 酱](http://sc.ftqq.com/)提供）  
   或者你可以打开 GitHub Actions 执行的全局邮件通知 <sup>[如何开启？](./how-to-enable-actions/#设置邮件提醒)</sup>，包括成功或失败信息

## Change Log

参阅 [Releases](https://github.com/JalinWang/HITsz-daily-report/releases) 列表。

## 声明

用户使用过程中输入的账户、密码等信息仅用做登陆认证凭据，脚本未对任何个人信息与登陆凭据进行非法留存、转发等操作，尽情放心使用。欢迎核查
