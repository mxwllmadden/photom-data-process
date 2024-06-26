rm(list = ls())

file_name = "A8 POST ETOH YES_5v6.csv"

setwd("C:\\Users\\Pitadmin\\Desktop\\csv files for ca imaging_paige\\ALL OF MARY'S CALCIUM IMAGING DATA\\VCA8 ETOH POST\\1v2")
pair = read.csv("C:\\Users\\Pitadmin\\Desktop\\csv files for ca imaging_paige\\ALL OF MARY'S CALCIUM IMAGING DATA\\VCA8 ETOH POST\\cc500_ A8 POST ETOH YES_1v2.csv", header = FALSE)

pair_cc100 = NULL
pair_cc100 = ccf(pair[,5], pair[,6], lag.max=500)
#acf_z = atanh(rvals)
#avg_acf = tanh(rowMeans(acf_z))
#max_z = apply(acf_z,2,max)

write.csv(pair_cc100$acf[], file = paste("cc500_",file_name))
#write.csv(avg_acf, file = "avg_acf_file_name_1_8.csv", row.names = FALSE)
#write.table(max_z, file = "max_z_file_name_1_8.csv", row.names = FALSE, col.names = FALSE, sep = ",")

#write.csv(avg_acf110, file = paste("avg_acf110_",file_name))