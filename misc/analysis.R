library(ggplot2)

avg.force <- c(0.169, 0.193, 0.353, 0.095, 0.087, 0.150, 0.098, 0.160)
se <- c(0.00289848832461, 0.002302172886644, 0.014203520690308,
        0.002441, 0.001732050807569, 0.006,
        0.005439056290694, 0.004358898943541)
mass <- c(15.4, 18.4, 23.3, 8.3, 6.5, 9.7, 8.6, 10.5)
mass.tf <- c(6.2, 7.0, 8.2, 4.1, 3.5, 4.6, 4.2, 4.8)#mass^(2/3)
data = data.frame(cbind(avg.force, mass.tf))
p <- ggplot(data, aes(mass.tf, avg.force)) + geom_point() +
  geom_errorbar(ymin = avg.force - se, ymax = avg.force + se) +
  scale_y_continuous(breaks = seq(0, 0.40, 0.05)) +
  scale_x_continuous(breaks = seq(3.0, 8.5, 0.5)) + 
  geom_smooth(method='lm') +
  labs(x = bquote(''*Mass^(2/3)*' / '*mg^(2/3)*''),
       y = 'Average Maximum Bite Force / N') + theme_bw() +
  theme(text=element_text(size=24,  family="Latin Modern Roman"),
        axis.title.x = element_text(margin = margin(t = 20)),
        axis.title.y = element_text(margin = margin(r = 20)))
png(filename='biteplot.png', width = 960, height = 480)
plot(p)
dev.off()




