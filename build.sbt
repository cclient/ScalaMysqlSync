name := "SqlSync"
version := "1.0"
scalaVersion := "2.12.2"
libraryDependencies += "mysql" % "mysql-connector-java" % "5.1.23"
libraryDependencies += "com.typesafe.slick" % "slick_2.12" % "3.2.0"
libraryDependencies += "org.slf4j" % "slf4j-nop" % "1.6.4"

libraryDependencies ++= Seq(
  "com.typesafe.akka" %% "akka-actor" % "2.5.2",
  "com.typesafe.akka" %% "akka-testkit" % "2.5.2" % Test
)

assemblyJarName in assembly := "SqlSync.jar"
mainClass in assembly := Some("main.task.Sync")
