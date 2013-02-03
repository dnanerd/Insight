
library(RMySQL)

#con2 <- dbConnect(MySQL(), user="testuser", password="testpass",dbname="yummly", host="localhost")
#dbGetQuery(con, "select count(*) from a_table")
matrix<-read.delim("~/Desktop/Work/Scripts/Insight/dummymatrix.txt",row.names=1)
matPos<-matrix[rowSums(matrix)>0,]
unitmatrix<-read.delim("~/Desktop/Work/Scripts/Insight/dummymatrix2.txt",row.names=1)
unitmatPos<-unitmatrix[rowSums(matrix)>0,]
removei = matPos[,'sugar']>10 | matPos[,'eggs']>5 | matPos[,'all.purpose.flour']>50 | matPos[,'butter']>10
