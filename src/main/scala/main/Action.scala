package main

/**
  * Created by cclient on 7/13/17.
  */
object Action extends Enumeration {

  //开始任务
  val MAIN_TASK_START=Value("start")
  //结束任务
  val MAIN_TASK_STOP=Value("stop")

  //开始全量比对
  val ONCEALL_TASK_START=Value("startByDiff")
  //递归拿全表
  val ONCEALL_GET=Value("getByOffset")
  //对比差量
  val ONCEALL_DIFF=Value("diffOrginDest")
  //差量入目标表
  val ONCEALL_INSERT=Value("insertWithOutUpsertLast")

  //开始增量比对
  val BYOFFSET_TASK_START=Value("start")
  //拿上一次的偏移
  val BYOFFSET_OFFSET_FROM_HISTORY_RECORD=Value("get")
  //如果拿偏移失败，则从目标取max(id)作偏移
  val BYOFFSET_OFFSET_FROM_DESTTABLE=Value("lastbydest")

  //从偏移位置开始读数据
  val BYOFFSET_GET=Value("sync")
  //取出数据添加到目标表
  val BYOFFSET_INSERT=Value("insertJust")
  //取出数据添加到目标表
  val BYOFFSET_INSERT_UPDATE=Value("insertOnDuplicateKey")
  //如果拿偏移失败，则从目标取max(id)作偏移
  val BYOFFSET_UPSERT_OFFSET=Value("upsert")
}
