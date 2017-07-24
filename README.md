##sql同步工具

###外采数据只提供数据，不提供查询服务(只能用基本的id查询)

###首先，项目以Mysql实现，slick支持其他数据库，代码生成脚本是完全以mysql的需求写的，如需其他sql服务同步需修改slick_generator.py

###此目标是多库多表异构同步（只字段类别相同，索引，主键，触发器等不同）

###最好的方案是用[canal](https://github.com/alibaba/canal)，但对方不提供mysql主从（技术上可行，但业务上对方不干）

###无奈只好用最原始的办法作同步,写个数据库表同步工具，没用scala写过sql操作，正好就拿来练手了

##基本概念

####源库OD，源表OT（orginal主）

####目的库DD，目的表DT(destination从)

####偏移表LT（保存每张表的上次同步到的id，保存在目的库DD

####数据同步依赖源表的自增id，同步数据时以id作电梯法实现

##流程

###启动每张表的同步服务

  * ####从last表先拿对应的上次的id,作为同步起始点
  
    * ####失败 查询相应目的表max(id)值，以这个值,作为同步起始点
    
    * ####成功 从OT offset同步起始点拿page_sise数据
    
      * #### 成功更新LT表中相应值

####遇到异常或拿到最后，则休眠段时间后重试       
       
##尚未完全自动化，需手动操作部分

###在DD建立last表（目前只实现了根据自增id同步，pub_time，spider_time冗余）

```chef
CREATE TABLE `last` (
  `table_name` char(20) NOT NULL,
  `id` bigint(20) DEFAULT NULL,
  `pub_time` datetime DEFAULT NULL,
  `spider_time` datetime DEFAULT NULL,
  PRIMARY KEY (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
* ###1 创建目标表，表结构与源表相同

* ###2 生成表对应实体及actor代码

* ###3 src/main/tables/下创建scala类文件，前一步生成的代码写入

* ###4 src/main/task/Sync.scala 添加表同步任务

##示例（代码生成脚本在tool下）

#### 1 执行 show create table from pdf

```sql
CREATE TABLE `pdf` (
  `id` int(11) NOT NULL,
  `engine` char(10) NOT NULL,
  `source_id` char(13) NOT NULL,
  `title` varchar(200) NOT NULL,
  `url` varchar(200) NOT NULL,
  `desc` varchar(500) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `source_id_UNIQUE` (`source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 2 添加至table_pdf.py

#### 3 执行python slick_generator.py 生成代码

#### 4 创建文件src/main/tables/Pdf.scala 前一步生成的代码写入

#### 5 修改src/main/task/Sync.scala下

```$xslt
类:class Sync
  方法:receive
添加 
 val pdfactor=context.actorOf(Props[PdfActor],"pdf")
 pdfactor !BYOFFSET_TASK_START
```

##部署启动服务

* ###1编译打包(结果为SqlSync.jar):

  ### sbt assembly
  
* ###2运行

  ### java -jar SqlSync.jar