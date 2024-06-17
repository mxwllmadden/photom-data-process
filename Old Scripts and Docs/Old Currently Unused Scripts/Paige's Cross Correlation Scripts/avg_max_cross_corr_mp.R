rm(list = ls())
setwd("F:\\")
rvals = read.csv("cc500_1_2.csv", col.names = FALSE)

acf_z = atanh(rvals)
avg_acf = tanh(rowMeans(acf_z))
max_z = apply(acf_z,2,max)

write.csv(avg_acf, file = "cross_corr_avg_cc10.csv", row.names = FALSE)    #this is r values for 500 timepoints 
write.csv(acf_z, file = "acf_z_cc10.csv", row.names = FALSE)  #z values for 500 timepoints 
write.table(max_z, file = "max_z_cc10_2_all.csv", row.names = FALSE, col.names = FALSE, sep = ",")  #


avg_acf110z =  matrix(nrow = lag_time*2 + 1, ncol = 2) #1st column is pair1, 2nd column is pair 2
avg_acf110 = matrix(nrow = lag_time*2 + 1, ncol = 2) #1st column is pair1, 2nd column is pair 2
max_acf20 = matrix(nrow = num_sweeps, ncol = 2) #1st column is pair1, 2nd column is pair 2
max_acf20z = matrix(nrow = num_sweeps, ncol = 2) #1st column is pair1, 2nd column is pair 2

write.csv(avg_acf110, file = paste("avg_acf110_",file_name))     #name of file with r values for full 100 timepoints
write.csv(avg_acf110z, file = paste("avg_z_acf110_",file_name)) #name of file with z values for full 100 timepoints
write.csv(max_acf20, file = paste("max_acf20_",file_name))     #name of file with r values for 20 timepoines
write.csv(max_acf20z, file = paste("max_z_acf20_",file_name))   #name of file with r values transformed to z values for 20 timepoints
