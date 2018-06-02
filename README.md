# bilibili-tools

挖坑开始

此项目为bilibili主站各项功能实现

另一已完成项目为bilibili直播站各功能实现 https://github.com/Dawnnnnnn/bilibili-live-tools



目前已实现:

    风纪委员投票
    每日投币
    每日登录
    每日分享
    每日观看



Q:观看，分享，投币的视频如何选取?

A:拉取关注列表，并在关注列表里up主投稿中随机选几个视频

Q:如何关闭自己不想要的功能?

A:
>

    tasks2 = [ 
        # judge().coin_run(),   # 投币任务
        judge().share_run(),  # 分享任务
        judge().watch_run(),  # 观看任务
        judge().judge_run()   # 仲裁案件]

将你不想开启的功能删掉或者注释掉即可

默认不打开投币功能，如想快速提高主站等级，把那一行注释去掉就可以了

挖坑结束，后期完善一下issue里提到的案件仲裁问题就没事了。