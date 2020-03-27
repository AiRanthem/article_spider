# 使用Crawl对拉勾网进行全站爬取
crawl是一种包装后的spider，通过定义一系列的rule，自动完成站点跳转
使用crawl，可以自动完成页面之间的跳转，我们只需要编写对应的解析函数、item、pipeline即可，
## 日记
1. 2020/3/27 开始项目
## 笔记
* 生成crawl爬虫

    1. 使用`scrapy genspider --list`可以查看自动生成的模板
    2. 使用`scrapy genspider -t <template> <name> <domain>`指定模板（这里使用crawl）
    
* crawl爬虫不能够重写 *parse* 方法。
    
    1. parse方法使用crawl实现的私有方法`_parse_response`
    2. `_parse_response`方法
        1. 首先调用`parse_start_url`函数对url的response进行处理
        2. 然后调用`process_results`方法对上一步的返回值进行解析
        3. 对上一步的返回值进行迭代，并yield
        3. 我们可以重写上述两个方法，否则此阶段什么都不发生。
        4. 接下来遍历我们定义的rules，每个迭代：
            1. 把response交给rule的LinkExtractor处理，生成下一步的一组链接
            2. 对上面生成的每个链接，yield一个Request
            3. crawl自己根据对应的rule对返回的Response做一些处理，然后回到最上面，周而复始。
            
* Rule

    | 参数 | 解释 |
    | :----: | :----: |
    |link_extractor|处理链接，下面详细解释
    |callback | 回调函数
    |cb_kwargs | 一些参数
    |follow|bool，是否需要进一步跟踪
    |process_links|链接预处理函数
    |process_request|request预处理函数
    
* LinkExtractor

    | 参数 | dtype | 解释 |
    | :----: | :----: | :----: |
    |allow|tuple of regex|url符合这个格式就解析
    |deny|tuple of regex|url符合这个格式就丢弃
    |allow_domains|tuple of regex|同上
    |deny_domains|tuple of regex|同上
    |restrict_xpaths|tuple of xpath|只在这些xpath范围内寻找
    |tags|tuple of string|寻找的标签
    |attrs|tuple of string|寻找的属性

    

