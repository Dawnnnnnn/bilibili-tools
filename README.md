# bilibili-tools

挖坑开始

此项目为 bilibili 主站各项功能实现

另一已完成项目为 bilibili 直播站各功能实现 https://github.com/Dawnnnnnn/bilibili-live-tools

目前已实现:

    <!-- 风纪委员投票 -->
    每日投币
    每日登录
    每日分享
    每日观看

Q:观看，分享，投币的视频如何选取?

A:拉取关注列表，并在关注列表里 up 主投稿中随机选几个视频

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

挖坑结束，后期完善一下 issue 里提到的案件仲裁问题就没事了。

懒的加那个投票阙值了。。。。案件仲裁直接删了....还想用的话就用上一个版本。。
