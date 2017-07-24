package main.task

import akka.actor.{Actor, ActorSystem, Props}
import main.tables._
import main.Action._

/**
  * Created by cclient on 6/2/17.
  */

class Sync extends Actor {
  override def preStart(): Unit = {
  }

  override def postStop(): Unit = println("first stopped")

  override def receive: Receive = {
    case MAIN_TASK_STOP => context.stop(self)
    case MAIN_TASK_START => {
//      val questionactor = context.actorOf(Props[QuestionActor], "question")
//      questionactor ! BYOFFSET_TASK_START
//
//      val answeractor = context.actorOf(Props[AnswerActor], "answer")
//      answeractor ! BYOFFSET_TASK_START
//
//      val commentactor = context.actorOf(Props[CommentActor], "comment")
//      commentactor ! BYOFFSET_TASK_START
//
//      val useractor = context.actorOf(Props[UserActor], "user")
//      useractor ! BYOFFSET_TASK_START
//
//      val topic_selectionActoractor = context.actorOf(Props[Topic_selectionActor], "topic_selectionActor")
//      topic_selectionActoractor ! ONCEALL_TASK_START
//
//      val boardactor = context.actorOf(Props[BoardActor], "board")
//      boardactor ! ONCEALL_TASK_START
//
//      val sub_boardActoractor = context.actorOf(Props[Sub_boardActor], "sub_boardActor")
//      sub_boardActoractor ! ONCEALL_TASK_START
    }
  }
}


object Sync {
  val system = ActorSystem.create("sqlsync")
  val Sync = system.actorOf(Props[Sync], "sync")
  val lastActor = system.actorOf(Props[LastActor], "lastActor")

  def main(args: Array[String]) = {
    Sync ! MAIN_TASK_START
  }
}

