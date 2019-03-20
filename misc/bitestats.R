library(ggplot2)
library(readxl)
setwd('~/Projects/portable-force-rig/misc')

get.datapoints <- function(data.set) {
  unique.weights <- unique(data.set[,2])
  out <- matrix(rep(0, length(unique.weights) * 2), ncol=2)
  for (i in 1:length(unique.weights)) {
    index <- data.set[,2] == unique.weights[i]
    out[i, 1] <- median(data.set[index, 1])
    out[i, 2] <- unique.weights[i]
  }
  out <- data.frame(out)
  colnames(out) <- c('x', 'y')
  return(out)
}

recalibrate <- function(data, curve, new.curve) {
  for (i in 1:length(data)) {
    index <- which.min(abs(curve - data[i]))
    data[i] <- new.curve[index]
  }
  return(data)
}


medium.5.curve <- read.csv('lookup/medium_5.csv')
medium.6.curve <- read.csv('lookup/medium_6.csv')
large.5.curve <- read.csv('lookup/large_5.csv')
large.6.curve <- read.csv('lookup/large_6.csv')

medium.5.curve.new <- read.csv('lookup/recalib_medium_5.csv')
large.5.curve.new <- read.csv('lookup/recalib_large_5.csv')
medium.6.curve.new <- read.csv('lookup/recalib_medium_6.csv')
large.6.curve.new <- read.csv('lookup/recalib_large_6.csv')

medium.5.data <- read.csv('train_data/medium_5.csv')
medium.6.data <- read.csv('train_data/medium_6.csv')
large.5.data <- read.csv('train_data/large_5.csv')
large.6.data <- read.csv('train_data/large_6.csv')

medium.5.datapoints <- get.datapoints(medium.5.data)
medium.6.datapoints <- get.datapoints(medium.6.data)
large.5.datapoints <- get.datapoints(large.5.data)
large.6.datapoints <- get.datapoints(large.6.data)

medium.5.x <- as.numeric(rownames(medium.5.curve.new)) - 1
medium.6.x <- as.numeric(rownames(medium.6.curve.new)) - 1
large.5.x <- as.numeric(rownames(large.5.curve.new)) - 1
large.6.x <- as.numeric(rownames(large.6.curve.new)) - 1

medium.5.frame <- data.frame(cbind(medium.5.x, medium.5.curve.new))
medium.6.frame <- data.frame(cbind(medium.6.x, medium.6.curve.new))
large.5.frame <- data.frame(cbind(large.5.x, large.5.curve.new))
large.6.frame <- data.frame(cbind(large.6.x, large.6.curve.new))

colnames(medium.5.frame) <- c('x', 'y')
colnames(medium.6.frame) <- c('x', 'y')
colnames(large.5.frame) <- c('x', 'y')
colnames(large.6.frame) <- c('x', 'y')

png(filename = 'recalib_large.png', width=960, height=480)
large.p <- ggplot(data=large.5.frame, aes(x, 1000 * y, color='Sensor 1')) +
  geom_line() +
  geom_line(data=large.6.frame, aes(x, 1000 * y, color='Sensor 2')) +
  geom_point(data=large.5.datapoints,
             aes(x, 1000 * y, color='Sensor 1'), size=2) + 
  geom_point(data=large.6.datapoints,
             aes(x, 1000 * y, color='Sensor 2'), size=2) + 
  labs(x = 'Raw sensor output',
       y = 'Force (mN)', color='') + theme_bw() +
  theme(text=element_text(size=24,  family="Latin Modern Roman"),
        axis.title.x = element_text(margin = margin(t = 20)),
        axis.title.y = element_text(margin = margin(r = 20))
  )

plot(large.p)
dev.off()

png(filename = 'recalib_medium.png', width=960, height=480)
large.p <- ggplot(data=medium.5.frame, aes(x, 1000 * y, color='Sensor 1')) +
  geom_line() +
  geom_line(data=medium.6.frame, aes(x, 1000 * y, color='Sensor 2')) +
  geom_point(data=medium.5.datapoints,
             aes(x, 1000 * y, color='Sensor 1'), size=2) + 
  geom_point(data=medium.6.datapoints,
             aes(x, 1000 * y, color='Sensor 2'), size=2) + 
  labs(x = 'Raw sensor output',
       y = 'Force (mN)', color='') + theme_bw() +
  theme(text=element_text(size=24,  family="Latin Modern Roman"),
        axis.title.x = element_text(margin = margin(t = 20)),
        axis.title.y = element_text(margin = margin(r = 20))
  )

plot(large.p)
dev.off()


data.table <- read_xlsx('~/Documents/max_force.xlsx', col_names = FALSE)
mass23 <- unlist(data.table[,1]) ^ (2/3)
mass23 <- round(mass23, 1)
avg.force <- c()
se <- c()
for (i in 1:nrow(data.table)) {
  bites <- unlist(data.table[i, -1])
  bites <- bites[bites > 0]
  if (i < 4) {
    bites <- recalibrate(bites, unlist(large.5.curve),
                         unlist(large.5.curve.new))
  } else {
    bites <- recalibrate(bites, unlist(medium.5.curve), 
                         unlist(medium.5.curve.new))
  }
  print(round(1000 * bites, 1))
  avg.force <- c(avg.force, mean(bites))
  se <- c(se, sd(bites) / sqrt(length(bites)))
}
avg.force <- 1000 * avg.force
se <- 1000 * se
frame <- data.frame(cbind(mass23, avg.force))

p <- ggplot(frame, aes(mass23, avg.force)) + geom_point() +
  geom_errorbar(ymin = avg.force - se, ymax = avg.force + se) +
  scale_y_continuous(breaks = seq(0, 400, 50)) +
  scale_x_continuous(breaks = seq(3.0, 8.5, 0.5)) + 
  geom_smooth(method='lm') +
  labs(x = bquote(''*Mass^(2/3)*' ('*mg^(2/3)*')'),
       y = 'Average Maximum Bite Force (mN)') + theme_bw() +
  theme(text=element_text(size=24,  family="Latin Modern Roman"),
        axis.title.x = element_text(margin = margin(t = 20)),
        axis.title.y = element_text(margin = margin(r = 20)))
png(filename='biteplotrecalib.png', width = 960, height = 480)
plot(p)
dev.off()
lm.fit <- lm(avg.force~mass23)
print(summary(lm.fit))

bite.data <- read_xlsx('~/Documents/154mg.xlsx')
bite.data <- unlist(bite.data)
t.axis <- 0.025 * (1:length(bite.data))
bite.data <- bite.data[t.axis >= 7 & t.axis <= 30]
t.axis <- t.axis[t.axis >= 7 & t.axis <= 30]
bite.data <- recalibrate(bite.data, unlist(large.5.curve),
                         unlist(large.5.curve.new))
t.axis <- 7 + 0.025 * (1:length(bite.data))
bite.data <- 1000 * bite.data
bite.sesh <- data.frame(cbind(t.axis, bite.data))


p <- ggplot(bite.sesh, aes(t.axis, bite.data)) +
  geom_line() +
  labs(x = 'Time (s)',
       y = 'Force (mN)') + theme_bw() +
  scale_y_continuous(breaks = seq(0, 200, 25)) +
  theme(text=element_text(size=24,  family="Latin Modern Roman"),
        axis.title.x = element_text(margin = margin(t = 20)),
        axis.title.y = element_text(margin = margin(r = 20)))
png(filename='bitesesh.png', width = 960, height = 480)
plot(p)
dev.off()
