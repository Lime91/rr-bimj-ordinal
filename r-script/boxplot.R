library(dplyr)
library(ggplot2)

data <- read.delim(
  "ebstatmax/data/Diacerein_study-setup.txt",
  header=TRUE,
  sep="",
  dec=",",
  na.strings = c("n/a")
)

data$Time2 <- recode(
  data$Time,
  t0="T1",
  t2="T2",
  t4="T3",
  t7="T4",
  t8="T5",
  t10="T6",
  t12="T7",
  t15="T8"
)
data$Group2 <- recode(data$Group, P="Placebo", V="Verum")

p <- data %>%
  ggplot(aes(x=Time2, y=Pain, fill=Group2)) + 
  geom_boxplot() +
  xlab("Time") + 
  labs(fill='Group') + 
  scale_fill_grey(start=0.8, end=0.95, na.value="red") +
  geom_vline(aes(xintercept=4.5)) +
  theme_classic() +
  geom_text(x=2.5, y=10, label="Period I") +
  geom_text(x=6.5, y=10, label="Period II")
ggsave("results/figure-3_pain.pdf", height=3.5)

p <- data %>%
  ggplot(aes(x=Time2, y=Pruritus, fill=Group2)) + 
  geom_boxplot() +
  xlab("Time") + 
  labs(fill='Group') + 
  scale_fill_grey(start=0.8, end=0.95, na.value="red") +
  geom_vline(aes(xintercept=4.5)) +
  theme_classic() +
  geom_text(x=2.5, y=10, label="Period I") +
  geom_text(x=6.5, y=10, label="Period II")
ggsave("results/figure-3_pruritus.pdf", height=3.5)
