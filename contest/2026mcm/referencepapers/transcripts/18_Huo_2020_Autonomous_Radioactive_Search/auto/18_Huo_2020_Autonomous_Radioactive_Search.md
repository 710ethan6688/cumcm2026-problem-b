Article

# Autonomous Search of Radioactive Sources through Mobile Robots

Jianwen Huo 1,2 , Manlu Liu 1, Konstantin A. Neusypin 2, Haojie Liu 1, Mingming Guo 1 and Yufeng Xiao 1,\*

Robot Technology Used for Special Environment Key Laboratory of Sichuan Province, Southwest University of Science and Technology, Mianyang 621010, China; huojianwen2008@hotmail.com (J.H.); liumanlu@swust.edu.cn (M.L.); liuhaojie\_work@163.com (H.L.); GUOMINGMING985@163.com (M.G.)

2 Bauman Moscow State Technical University, Moscow 105005, Russia; neysipin@mail.ru

\* Correspondence: xiaoyf\_swit1@163.com

Received: 31 May 2020; Accepted: 17 June 2020; Published: 19 June 2020

![](images/6de94fb7219e09f9f22b2e3d3b5ba96905e21343edee2df592cfac2693d54d1d.jpg)

Abstract: The research of robotic autonomous radioactivity detection or radioactive source search plays an important role in the monitoring and disposal of nuclear safety and biological safety. In this paper, a method for autonomously searching for radioactive sources through mobile robots was proposed. In the method, by using a partially observable Markov decision process (POMDP), the search of autonomous unknown radioactive sources was realized according to a series of radiation information measured by mobile robot. First, the factors affecting the accuracy of radiation measurement during the robot’s movement were analyzed. Based on these factors, the behavior set of POMDP was designed. Secondly, the parameters of the radioactive source were estimated in the Bayesian framework. In addition, through the reward strategy, autonomous navigation of the robot to the position of the radiation source was achieved. The search algorithm was simulated and tested, and the TurtleBot robot platform was used to conduct a real search experiment on the radio source Cs-137 with an activity of 37 MBq indoors. The experimental results showed the effectiveness of the method. Additionally, from the experiments, it could been seen that the robot was affected by the linear velocity, angular velocity, positioning accuracy and the number of measurements in the process of autonomous search for the radioactive source. The proposed mobile robot autonomous search method can be applied to the search for lost radioactive sources, as well as for the leakage of substances (nuclear or chemical) in nuclear power plants and chemical plants.

Keywords: autonomous search; radioactive sources; POMDP; measurement error model; mobile robot

## 1. Introduction

For more than half a century, nuclear energy and nuclear technology have been steadily developed in the world. Nuclear energy plays an important role in optimizing the energy structure, ensuring energy security, promoting pollution reduction and responding to climate change, etc. Radioactive materials have been widely used in the fields of industry, agriculture, national defense, medical treatment and scientific research, which have effectively promoted national production and economic and social development. However, in the process of nuclear energy and nuclear technology application, if a nuclear radiation accident occurs, it will pose a great threat to social security and the country’s political economy, easily causing large-scale casualties and widespread social panic.

According to statistics from the International Atomic Energy Agency (IAEA) [1], as of 31 December 2019, more than 3686 nuclear accidents have been confirmed by the Illegal Traffic Database (ITDB) on theft of nuclear and radioactive materials and other illegal activities. Therefore, it is an important safety issue in the application of nuclear technology to detect the radioactive distribution of radioactive sources in space, and quickly search for and remove nuclear radioactive materials in scattered areas.

Although researchers have been paying attention to this topic for more than two decades, the detection and search of unknown radioactive sources is still a challenging operation in real environment. The main difficulties come from: (1) If the missing or stolen radioactive source is searched by operation personnel, it will increase the operation time and operator’s health risk [2]; (2) if it is searched by a robot, due to the unknown position and direction of the radioactive source and limited perspective of the robot’s observation, the search process is very difficult [3].Therefore, in this paper, an autonomous search algorithm for unknown radioactive sources is designed by using a partially observable Markov decision process (POMDP). The main contributions of this paper are as follows: (1) The robot radiation measurement error model is established, and the factors that affect the radiation measurement results during the movement of the robot are found, which helps the design of the autonomous search algorithm in the later stage. (2) The coordinate, direction of the detection point and detector count of the robot at the current moment are taken as current knowledge, and the posterior probability density function (PDF) of radioactive source parameters is used as the information status in the POMDP. The next action of the robot is selected through the reward strategy of information entropy. (3) The Markov chain Monte Carlo (MCMC) method is used to improve the particle filter to approximate the calculation of PDF, thereby completing the importance sampling of particles.

To study the above topics, this paper is organized as follows: In Section 2, related research in this area is investigated. In Section 3, the error model analysis of robotic radiation measurement is performed. In Section 4, based on the error measurement model, an autonomous search algorithm for unknown radioactive sources is designed. In Section 5, simulation and real experiments are performed. Finally, the conclusions and shortcomings are described.

## 2. Prior Work

In this section, a survey of literature on radioactive source parameter estimation and search strategies is conducted. The search of search strategies is not only about radioactive sources in nuclear physics, but also gas diffusion sources (including biochemistry).

## 2.1. Estimation of Source Parameter

The essence of parameter estimation is to calculate the position and Source Term Parameter of the radioactive source. The traditional method uses measured values of nuclear radiation detectors to determine whether there is a radioactive source in a certain area, and then measures multiple measurement points, and uses the least square method [4,5] or geometric method [5–7] to estimate the position and the intensity of the radioactive source. In addition, in [4], the position is correlated with the count rate of the detector; and the change of radiation source position and the deviation between the measured value and the model prediction are also considered. In [5], several probabilistic methods are also provided to estimate the position and intensity of the radioactive source, such as maximum likelihood estimation. In [6], a combined geometric positioning method and sequential probability ratio test are used for radioactive source positioning. Traditional methods rely on the sensitivity of the detector.

In addition, according to the principle of mathematical statistics, radioactive decay occurs randomly, but follows a certain statistical distribution (Poisson distribution or normal distribution), so when estimating the parameters of a radioactive source, the measured value of the detector can be described as a random variable, just like the maximum likelihood estimation method in [5,8]. But when there are three or more radioactive sources at the same time, the maximum likelihood estimation method is not applicable. In addition, the higher SNR thresholds are also considered to be its shortcomings. In [8–13], the Bayesian estimation algorithm was used to make up for the shortcomings of the maximum likelihood estimation method. According to Bayesian theory, the posterior probability distribution of the parameter vector of the radioactive source is constructed from the observation data in the radiation field. Therefore, the information of the radioactive source is obtained by solving the posterior probability distribution, which can be approximated and represented by importance sampling [8], progressively corrected importance sampling [11], particle filtering [9,10] and MCMC methods [12,13]. It is worth noting that [12] revealed that the accuracy of the measurement count rate is closely related to the orientation of the detector, which provides a good idea for the error analysis of robotic radiation measurement.

In addition to the above two methods, a Gaussian mixture model is also used to characterize the radiation field and establish a radiation map. Using a logarithmic gradient classifier, the local graph is segmented into several positions of interest to perform radioactive source localization [14]. In the chaotic 3D environment [15], a method of drawing a spatial distribution map of radiation in the environment using a gamma camera was proposed. The source can be effectively found and located according to the spatial distribution map.

## 2.2. Search Strategy

The simplest method for a search strategy is to search in a fixed manner within a specific area. For example, in [7] the UAV was used to detect radioactive materials after the nuclear power plant accident. The UAV moved in a circular trajectory in the air, and estimated the position of the radioactive source as a centroid, which is calculated by using the detected dose of three points. The three-point positioning method has very high requirements on the detector’s response time. If the response time is long, the estimation error will be very large. In [16–19] the detector was mounted on the UAV to search in a traversal manner. The advantage of this method is that it does not require prior estimation of the radioactive source’s parameters, and the search accuracy was high, but the search efficiency was low. In order to save time and maximize the search efficiency, [19] also proposed the binary search method and the successive approximation search method. The binary search method is suitable for radioactive sources with high activity. Compared with the traversal search algorithm, it was implemented by discarding half of the area at a time, which greatly reduces search time. The successive approximation search method required the activity of the radioactive source to be higher, because it needs to detect a significant change in dose rate at the boundary of the region.

The second method of a search strategy is based on behavior and criteria [20–22]. For example, [20] used behavior-based navigation, combining data detected from previously visited areas. This allows the robot to detect safely and effectively. The study in [21] introduced a new behavior-based method for navigating mobile robots in an unknown environment. In this method, each behavior was implemented by a fuzzy controller and executed independently. The authors in [22] constructed a behavior-based control system architecture for the detection of radioactive hot spots under the limitation of sensors. Such methods need to define robot-related behaviors before searching, such as avoiding collisions, detecting radioactive sources and so on. The robot took corresponding actions based on the perceived environmental characteristics and defined criteria until the source item was searched. Such methods are difficult to apply to unknown environments because it is difficult to design behaviors and norms in that conditions.

The third method is as follows. The robot moves randomly or in a fixed manner for a period of time in the search area. With the sensor sensing the radiation information, the source position is calculated by using the source parameter estimation method during this period. Then, combining the methods of information gain [9,10,23], information entropy [24], artificial potential field [25,26], etc., the robot could move to the target point. It is worth noting that in [26], when detecting gamma rays, the incidence angle of the sensor affected the measured radiation intensity. This method required very high accuracy of the source item estimation. If the estimation is not accurate, the robot cannot find the source. The dynamically updated search method [27–32] can make up for this shortcoming well. For example, in [27] the dynamic programming method for robot chemical source tracking was proposed. The robot searched for chemical sources based on real-time wind speed and the estimated chemical gas concentration. In [28], in the Bayesian framework, the search efficiency was improved by using the semantics between the detected and recognized gas and the objects in the environment. In addition, the probability of detection and recognition was correlated with the robot’s current position and target distance though using the Markov decision process, to minimize the search time. In [29–32], POMDP was used to design the gas source search algorithm and the Bayesian frame was used to estimate the gas source parameters. PDF acted as the information state in POMDP, and the gas source search was completed through the reward mechanism and behavior selection. In [29,30] three reward mechanisms were provided: information entropy, Infotaxic II and Bhattacharyya distance. In [31], relative entropy (also known as Kullback–Leibler divergence) was used as a reward for POMDP. The authors in [32] combined the potential energy and the entropy into free energy to be minimized as the reward of POMDP. The studies in [29–32] provided good ideas for the autonomous search algorithm for radioactive sources in this paper.

This paper uses POMDP to design a method for robots to autonomously search for unknown radioactive sources, but the differences from the above reference are: (1) This paper establishes an error model of the nuclear radiation measurement of the robot during the search process and analyzes the influence of the robot’s speed, positioning accuracy and detection angle on the unknown radioactive source position estimation. (2) In this paper, the speed and angular velocity of the robot are related together as a limited set of actions for POMDP. However, in reference [29–32] the POMDP behavior set was a single direction indicating behavior, such as $\{ . , \uparrow , \to , \downarrow ,  \}$ . The limited action set method provided in this paper can make the robot more maneuverable in the search process. (3) The current knowledge is related to the direction of robot movement, rather than a single coordinate and detector count, and the MCMC method was used to improve the particle filter to approximate the posterior, and then complete the importance sampling of the particles.

## 3. Analysis of Robotic Radiation Measurement Model

## 3.1. Radiation Measurement Principle

Assuming that the lost or stolen radioactive source is approximately a point, so only the source activity and spatial location are considered in the study, and the spatial volume is not considered. In homogeneous air, the exposure dose rate of the γ-ray source at distance R is [33]: $\begin{array} { r } { \dot { X } = \frac { d X } { d t } = \Gamma \frac { A } { R ^ { 2 } } } \end{array}$ Among them, X is the exposure; Г and A is the exposure dose rate constant and the activity of the point radiation source, respectively; $R ^ { 2 } = { \left( x _ { i } - x _ { 0 } \right) } ^ { 2 } + { \left( y _ { i } - y _ { 0 } \right) } ^ { 2 } .$ , where $x _ { 0 } , y _ { 0 }$ is the source coordinate. The dose equivalent rate $\dot { H } ( \mu S v / h )$ of γ radiation source at distance R can be obtained from Equation (1),

$$
\dot { H } = { \frac { d H } { d t } } = { \frac { d ( w D ) } { d t } } = { \frac { d ( w f X ) } { d t } } = \Gamma w f { \frac { A } { R ^ { 2 } } } ,\tag{1}
$$

where w is the radiation weighting factor, and the value of photon and electron is $1 ; D$ is the absorbed dose; f is the conversion factor for converting exposure into absorbed dose.

The radioactive decay of radioactive materials generally occurs randomly, but within a certain time interval, through the statistics of a large number of atoms, it can be found that the decay process is subject to certain statistical laws. In radiation measurement, the number of radioactive particles emitted by a radioactive source in a unit time can be detected. This process has statistical fluctuations in radioactive counts and obeys the Poisson distribution [9],

$$
P \Big ( C _ { p m } , \lambda \Big ) = \frac { \lambda ^ { C _ { p m } } } { C _ { p m } ! } e ^ { - \lambda } ,\tag{2}
$$

where $C _ { p m } \in N ^ { + }$ is the count rate per minute $( \mathrm { m i n } ^ { - 1 } )$ of the detector, which represents the detected count value within a minute; $\lambda = \eta M ,$ , where M is the average value of multiple measurements of N

particles generated by the decay of the radioactive source in a certain time interval;environmental media [34] bring difficulty to the position estimation. Therefore, it $\eta$ is the efficiencynecessary to fin of the detector.the factors th $C _ { p m }$ can be calculated from Equation (3),nterfere with the robot’s radiation

$$
C _ { p m } = \dot { H } \times E n e r g y n u m b e r ,\tag{3}
$$

where Energynumber is energy response constant [5].  ̇ =

## 3.2. Error Analysis of Robotic Radiation Measurement Model

The position of the radiation source is estimated by using Equation (1) after the robot measures multiple points. However, factors such as the detection angle, detection distance, detection time and environmental media [34] bring difficulty to the position estimation. Therefore, it is necessary to find the factors that interfere with the robot’s radiation measurement and reduce the measurement  =     . uncertainty during the movement.

Assume that the motion model of the mobile robot is differential motion model, that is:Among them,   is the distance from point B to the radioactive source;   is th

$$
\left\{ \begin{array} { l } { \dot { x } = v \cos \theta } \\ { \dot { y } = v \sin \theta } \\ { \dot { \theta } = \omega } \end{array} \right. ,\tag{4)ativ}
$$

where $x , y , \theta$ are robot position and direction; v is linear velocity; ω is angular velocity. Assume that the robot is at point $\textbf { A } \left( x _ { 1 } , y _ { 1 } \right)$ at time $t _ { 0 } ,$ and moves to point $\mathrm { ~ B ~ } ( x _ { 2 } , y _ { 2 } )$ at time $t _ { 1 }$ (shown in Figure 1), where $t _ { 1 } = \beta \Delta t$ . According to the principle of triangle, we can get  =     ( ∆ )  ,

$$
d _ { 2 } = l { \frac { \sin \varphi _ { 1 } } { \sin ( \varphi _ { 2 } - \varphi _ { 1 } ) } } \ .\tag{5) }
$$

![](images/5e087c75f59a927ea2b9737e5dad4daa1394deb5ebaf6cd462723f6d0bc4e500.jpg)  
Figure 1. Robot’s radiation measurement modeFigure 1. Robot’s radiation measurement model.

Among them, $d _ { 2 }$ is the distance from point B to the radioactive source; l is the distance between point A and point ${ \tt B } , l ^ { 2 } = \left( x _ { 2 } - x _ { 1 } \right) ^ { 2 } + \left( y _ { 2 } - y _ { 1 } \right) ^ { 2 } ; \varphi _ { 1 } ( \varphi _ { 2 } )$ is the angle between the line connecting the point (A or B) and the radiation source and the direction of the robot’s movement. It should be noted ∆  =   ∆  +   ∆  +   ∆  =   (  − ∆       + ∆       + ∆       ) , (7here that the detector is installed directly in front of the robot and there is no relative displacement   between the detector and the robot, so the robot’s moving direction is the detection orientation. Robot movement is a continuous process, and $\varphi _ { 2 }$ changes with time, so ϕ2 can be approximated by the least squares polynomial form as

$$
\varphi _ { 2 } = \sum _ { j = 0 } ^ { p - 1 } a _ { j } ( \beta \Delta t ) ^ { j } \ : ,\tag{6}
$$

where $a _ { j }$ is polynomial coefficient, $\begin{array} { r } { a _ { 1 } = \dot { \varphi } = \frac { v \sin \varphi _ { 1 } } { d _ { 2 } } , a _ { 2 } = \frac { 1 } { 2 ! } \dot { \varphi } = \frac { 1 } { 2 } \frac { 2 v ^ { 2 } \sin \varphi _ { 1 } \cos \varphi _ { 1 } } { d _ { 2 } ^ { 2 } } = \dot { \varphi } _ { 1 } ^ { 2 } \cot \varphi _ { 1 } , \varphi = \varphi _ { 2 } - \varphi _ { 1 } ; } \end{array}$ $p$ is fitting times; β is time interval coefficient.

According to Equation (5), the error model $\Delta d _ { 2 }$ of the linear approximation of the distance $d _ { 2 }$ from point B to the radiation source is,

$$
\Delta d _ { 2 } = \frac { \partial d _ { 2 } } { \partial l } \Delta l + \frac { \partial d _ { 2 } } { \partial \varphi } \Delta \varphi + \frac { \partial d _ { 2 } } { \partial \varphi _ { 1 } } \Delta \varphi _ { 1 } = d _ { 2 } \Biggl ( \frac { \Delta l } { l } - \Delta \varphi _ { 2 } \cot \varphi + \Delta \varphi _ { 1 } \cot \varphi + \Delta \varphi _ { 1 } \cot \varphi _ { 1 } \Biggr ) ,\tag{7}
$$

where $\Delta l , \Delta \varphi _ { 1 } , \Delta \varphi _ { 2 }$ are the errors of $l , \varphi _ { 1 } , \varphi _ { 2 }$ , respectively. It is not difficult to see from Equation (7) that the positioning error of the radiation source is related to the robot self-positioning, the angle between the line connecting the γ-ray source and the sensor and the direction of the sensor’s movement, and whether other factors are related needs further discussion. Assume that the anticipation error of positioning and incidence angle is zero and they are not related to each other, so

$$
\left\{ \begin{array} { c } { { E \big [ \frac { \Delta { d } _ { 2 } } { { d } _ { 2 } } \big ] = 0 } } \\ { { \sigma _ { \Delta { d } _ { 2 } } ^ { 2 } = \frac { \sigma _ { \Delta { l } } ^ { 2 } } { l ^ { 2 } } + \sigma _ { \varphi _ { 2 } } ^ { 2 } \cot ^ { 2 } \varphi + \big ( \cot ^ { 2 } \varphi + \cot ^ { 2 } \varphi _ { 1 } \big ) \sigma _ { \varphi _ { 1 } } ^ { 2 } } } \end{array} \right. .\tag{8}
$$

Among them, $\sigma _ { \Delta l ^ { \prime } } ^ { 2 } \sigma _ { \varphi _ { 2 } } ^ { 2 } , \sigma _ { \varphi _ { 1 } } ^ { 2 }$ are the measurement variance of the corresponding parameters, and their value are unknown. The distance l between point A and point B is a function of $x _ { 1 } , y _ { 1 } , x _ { 2 } ,$ , y2. The linear approximation model error ∆l is obtained as $\begin{array} { r } { \Delta l = \dot { \frac { \partial l } { \partial x _ { 1 } } } \Delta x _ { 1 } + \frac { \partial l } { \partial y _ { 1 } } \Delta y _ { 1 } + \frac { \partial l } { \partial x _ { 2 } } \Delta x _ { 2 } + \frac { \partial l } { \partial y _ { 2 } } \Delta { y _ { 2 } } } \end{array}$ 2 , so the variance $\sigma _ { \Delta l } ^ { 2 }$ is calculated as

$$
\sigma _ { \Delta l } ^ { 2 } = ( \sigma _ { \Delta x _ { 1 } } ^ { 2 } + \sigma _ { \Delta x _ { 2 } } ^ { 2 } ) \cos ^ { 2 } \theta + ( \sigma _ { \Delta y _ { 1 } } ^ { 2 } + \sigma _ { y x _ { 2 } } ^ { 2 } ) \sin ^ { 2 } \theta .\tag{9}
$$

According to [35], $\begin{array} { r } { \sigma _ { \Delta x _ { 1 } } ^ { 2 } = \sigma _ { \Delta y _ { 1 } } ^ { 2 } = \frac { 4 \sigma _ { p } ^ { 2 } } { N } } \end{array}$ , where $\sigma _ { p } ^ { 2 }$ is the measurement variance of the position sensor, N is the number of measurements. $\begin{array} { r } { \sigma _ { \Delta x _ { 2 } } ^ { 2 } = \sigma _ { \Delta y _ { 2 } } ^ { 2 } = \frac { 4 \sigma _ { p } ^ { 2 } } { N } \Big ( 1 + 3 \frac { \beta ^ { 2 } } { N } \Big ) . ~ \sigma _ { \varphi _ { 1 } } ^ { 2 } = \frac { 4 \sigma _ { \varphi } ^ { 2 } } { N } } \end{array}$ , where $\sigma _ { \varphi } ^ { 2 }$ is the measurement variance of the incident angle between the γ-ray and the sensor. From Equation (6),

$$
\sigma _ { \varphi _ { 2 } } ^ { 2 } = \sigma _ { \Delta a _ { 0 } } ^ { 2 } + \sigma _ { \Delta a _ { 1 } } ^ { 2 } ( \beta \Delta t ) ^ { 2 } + \cdots + \sigma _ { \Delta a _ { p } } ^ { 2 } ( \beta \Delta t ) ^ { 2 p } + \cdots\tag{10}
$$

when $p = 2$ , combined with the literature [35], Equation (10) can be rewritten as

$$
\sigma _ { \varphi _ { 2 } } ^ { 2 } = \frac { 4 \sigma _ { \varphi } ^ { 2 } } { N } + \frac { 1 2 \sigma _ { \varphi } ^ { 2 } } { N ^ { 3 } \Delta t ^ { 2 } } ( \beta \Delta t ) ^ { 2 } + \sum _ { j = 2 } ^ { \infty } a _ { j } ^ { 2 } ( \beta \Delta t ) ^ { 2 j } \ : .\tag{11}
$$

According to the Lagrange multiplier, Equation (11) can be obtained in the final form as

$$
\sigma _ { \varphi _ { 2 } } ^ { 2 } = \frac { 8 \sigma _ { \varphi } ^ { 2 } } { N } + \frac { 1 2 \sigma _ { \varphi } ^ { 2 } } { N ^ { 3 } \Delta t ^ { 2 } } \big ( \beta \Delta t \big ) ^ { 2 } .\tag{12}
$$

In addition, the distance l between point A and point B can be determined according to the robot’s speed v, that is,

$$
l = v ( \beta + N ) \Delta t .\tag{13}
$$

Similarly, cot $\begin{array} { r } { \varphi = \frac { d _ { 2 } } { v \sin \varphi _ { 1 } ( \beta + N ) \Delta t } = \frac { 1 } { \dot { \varphi } ( \beta + N ) \Delta t } . } \end{array}$ According to Equations (8)–(14), $\sigma _ { \Delta d _ { 2 } } ^ { 2 }$ can be calculated as

$$
\sigma _ { \Delta d _ { 2 } } ^ { 2 } = { \frac { 4 { \left( 2 + 3 { \frac { \beta } { N ^ { 2 } } } \right) } } { N { \left( \beta + N \right) } ^ { 2 } } } \Biggl ( { \frac { \sigma _ { p } ^ { 2 } } { v ^ { 2 } \Delta t ^ { 2 } } } + { \frac { \sigma _ { \varphi } ^ { 2 } } { \dot { \varphi } ^ { 2 } \Delta t ^ { 2 } } } \Biggr ) + { \frac { 4 \sigma _ { \varphi } ^ { 2 } } { N } } \cot ^ { 2 } \varphi _ { 1 } .\tag{14}
$$

During the measurement, $\sigma _ { \Delta d _ { 2 } } ^ { 2 }$ needs to be minimized, so use the following formula to get the value of $\beta \colon$

$$
{ \frac { d ( { \frac { 4 ( 2 + 3 { \frac { \beta } { N ^ { 2 } } } ) } { N ( \beta + N ) ^ { 2 } } } ) } { d \beta } } = 0  \beta = { \frac { 2 N } { 3 } } .\tag{15}
$$

Bring Equation (15) into Equation (14), so

$$
\sigma _ { \Delta d _ { 2 } } ^ { 2 } = \frac { 2 4 } { 5 N ^ { 3 } } \Bigg ( \frac { \sigma _ { p } ^ { 2 } } { v ^ { 2 } \Delta t ^ { 2 } } + \frac { \sigma _ { \varphi } ^ { 2 } } { \dot { \varphi } ^ { 2 } \Delta t ^ { 2 } } \Bigg ) + \frac { 4 \sigma _ { \varphi } ^ { 2 } } { N } \cot ^ { 2 } \varphi _ { 1 } .\tag{16}
$$

From Equation (16), we can see that the robot’s positioning accuracy of the radioactive source during the movement is affected by the number of measurements, the measurement accuracy of position sensor, the angle between the line connecting the gamma ray and the measurement sensor and the direction of the sensor’s movement, and the speed of the robot. By analyzing the factors that affect the positioning of the radioactive source, it provides help for the following mobile robot radioactive source positioning strategies.

## 4. Unknown Radioactive Source Search Strategy

## 4.1. Search Strategy

The position of the radioactive source is initially unknown for a searching robot. Based on its own perception of the surrounding environment, by using the local information for path planning, the robot could finally find the unknown radioactive sources. Furthermore, since radioactive source is strictly controlled items, if it gets lost, its number is generally known. Therefore, in this paper, we just consider the case of a single lost radioactive source.

Robot autonomous search strategy was designed using POMDP [36] in this paper. In POMDP model, the robot needs to collect environmental information (observation values) through sensors to update its credibility on the current state, which is the basis for the robot’s decision on the next action choice. According to Equations (3) and (4), the observation sequence of the sensor when the robot moves to the target point is established, that is, $z _ { 1 : k } = \{ z _ { 1 } , z _ { 2 } , z _ { 3 } , \cdots , z _ { k } \}$ , where $z _ { k } = ( x _ { k } , y _ { k } , \theta _ { k } , C _ { p m k } ) ^ { T }$ represents the measurement value $C _ { p m k }$ obtained by the robot at a certain position $( x _ { k } , y _ { k } )$ and in a certain direction $\theta _ { k } .$ Assume the parameter vector I of the unknown radioactive source is $\boldsymbol { I } = \left( x _ { 0 } , y _ { 0 } , \theta _ { 0 } , I \right) ^ { T }$ where x0, y0 is the coordinate of the plane position, $\theta _ { 0 }$ is the included angle of the radiation source with respect to the movement direction of the starting point of the robot, I is the activity of radioactive source and the unit is Bq. According to Bayes’ rule, the likelihood function of the observation sequence $z _ { 1 : k }$ is,

$$
p ( z _ { 1 : k } | I ) = \prod _ { i = 1 } ^ { k } p ( z _ { i } | I ) ,\tag{17}
$$

among them, $p ( z _ { i } | I ) = P \big ( C _ { p m i } , \lambda _ { i } \big )$ Furthermore, according to Bayesian theory, after obtaining the observation sequence $z _ { 1 : k }$ in the radiation field, the posterior probability distribution function of the radiation source’s parameter vector I can be obtained as $p ( I | z _ { 1 : k } )$ . Since the searching action of

radioactive source is a gradual process, the asymptotic calculation formula of the posterior probability distribution function is as follows:

$$
p ( I | z _ { 1 : k } ) = \frac { p ( z _ { i } | I , z _ { 1 : i - 1 } ) p ( I | z _ { 1 : i - 1 } ) } { p ( z _ { i } | z _ { 1 : i - 1 } ) } , 1 \leq i \leq k ,\tag{18}
$$

Then, according to Equation (18), the information state of discrete time $k + 1$ can be obtained as

$$
p \big ( I | z _ { 1 : k + 1 } \big ) = \frac { p \big ( z _ { i + 1 } \big | I \big ) p ( I | z _ { 1 : k } ) } { \int p \big ( z _ { i + 1 } \big | I \big ) p ( I | z _ { 1 : k } ) d I } , 1 \leq i \leq k .\tag{19}
$$

In addition, when $k = 0 , p ( I )$ is the prior distribution of the source’s parameters. At first, it was thought that unknown radioactive sources could be located anywhere in the search area and could be set to be evenly distributed. Next, after making certain judgments based on local information, the robot needs to continue moving to make further observation records until the radioactive source is searched. Then the robot’s finite action set is defined as $A = \{ ( v , \Delta \theta ) , ( - v , \Delta \theta ) , ( v , - \Delta \theta ) , ( - v , - \Delta \theta ) , ( v , 0 ) , ( - v , 0 ) , ( 0 , \Delta \theta ) , ( 0 , - \Delta \theta ) , ( 0 , 0 ) \}$ , where $\Delta \theta$ is the robot’s rotation angle within the time step ∆t, which is determined by the angular velocity $\omega ,$ that is, $\Delta \theta = \omega \Delta t$ . Thus, the finite action set can be simplified as $A = \{ ( v , \omega ) , ( - v , \omega ) , ( v , - \omega ) , ( - v , - \omega ) , ( v , 0 ) \}$ $( - v , 0 ) , ( 0 , \omega ) , ( 0 , - \omega ) , ( 0 , 0 ) \}$ .Then the position and direction of the robot at time $k + 1$ can be obtained from Equation (20),

$$
\left\{ \begin{array} { c } { x _ { k + 1 } = x _ { k } + \Delta t v \cos { \theta _ { k } } } \\ { y _ { k + 1 } = y _ { k } + \Delta t v \sin { \theta _ { k } } } \\ { \theta _ { k + 1 } = \theta _ { k } + \Delta t \omega } \end{array} \right. .\tag{20}
$$

According to Equation (20), the measurement value $z _ { k + 1 }$ of the sensor at time $k + 1$ depends on the position and direction at time k and the selected action a $( a \in A )$ . Within each time step $\Delta t ,$ the robot should move in the direction where the expected count rate is maximum. Therefore, this paper uses information entropy to describe the reward of action a. Then the robot’s information entropy during the search process changes to [37],

$$
D ( a _ { k } ) = - P r _ { k } S _ { k } + ( 1 - P r _ { k } ) \bigl ( \mathrm { E } ( S _ { k + 1 } ) - \mathrm { S } _ { k } \bigr ) ,\tag{21}
$$

where $\mathsf { S } _ { k }$ is the information entropy of the radioactive source, that is, $\begin{array} { r } { { \sf S } _ { k } = \int { p ( { \cal I } | z _ { 1 : k } ) \log p ( { \cal I } | z _ { 1 : k } ) d { \cal I } } } \end{array}$ and $P r _ { k }$ can be calculated using the kernel density estimation method [38]. The physical meaning of Equation (21) is explained in [37]. The first term on the right side of the formula indicates that the robot has found the radioactive source at time $k + 1$ , while the second term indicates that the robot has not yet searched the source at time $k + 1 ,$ and needs further searching until the source is found, so $\mathsf { S } _ { k + 1 } = 0 .$ , and in the search process, only the second term of Equation (21) is used to represent the reward. According to the Equation (2), the expectation of the Shannon entropy $\mathsf { S } _ { k + 1 }$ of measured value $z _ { k + 1 }$ at the time $k + 1$ can be obtained as

$$
\mathrm { E } ( \mathsf { S } _ { k + 1 } ) = \sum _ { C _ { p m } = 0 } ^ { C _ { p m } } P \big ( C _ { p m } , \lambda \big ) \mathsf { S } _ { k + 1 } = \sum _ { \lambda _ { k + 1 } = 0 } ^ { C _ { p m } } p \big ( z _ { k + 1 } \big | I \big ) \int p \big ( I \big | z _ { 1 : k + 1 } \big ) \log p \big ( I \big | z _ { 1 : k + 1 } \big ) d I .\tag{22}
$$

Then, while the robot is looking for a radioactive source, according to the optimal strategy $\pi _ { k } { } ^ { * }$ $D ( a _ { k } )$ is minimized, that is,

$$
\pi _ { k } { } ^ { * } = a r g m i n D ( a _ { k } ) .\tag{23}
$$

## 4.2. Parameter Estimation of Radioactive Sources

Using a mobile robot to search for radioactive sources is a gradual process, and the radioactive source parameters are gradually estimated according to the search strategy of Section 4.1. However, in the search strategy, the posterior probability distribution function is difficult to obtain analytically. Therefore, the MCMC method is used to improve the particle filter to approximate the posterior probability distribution function. The basic idea of the particle filtering algorithm is to use a group of n particles with their own weights $\Big \{ { I } _ { k } ^ { i } , w _ { k } ^ { i } \Big \} , i = 1 , \cdots$ , n to approximate the posterior probability density $p ( I | z _ { 1 : k } )$ of the radioactive source parameter I. In addition, the weight of the particles satisfies $\begin{array} { r } { \sum _ { i = 1 } ^ { n } w _ { k } ^ { i } = 1 } \end{array}$ . Then the posterior probability density is approximately as follows:

$$
p ( \pmb { I } | \boldsymbol { z } _ { 1 : k } ) \approx \sum _ { i = 1 } ^ { n } w _ { k } ^ { i } \delta \big ( \pmb { I } - \pmb { I } _ { k } ^ { i } \big ) ,\tag{24}
$$

where $\delta ( \cdot )$ is a Dirac function. Based on this approximation, complex integration operations can be converted into sum operations, such as $\begin{array} { r } { \mathsf { S } _ { k } \approx - \sum _ { i = 1 } ^ { n } w _ { k } ^ { i } } \end{array}$ log $w _ { k } ^ { i }$ . Assume that the importance sampling density is $q ( I | z _ { 1 : k } )$ , the prior probability transfer distributionis is chosen as $q ( I _ { k } | I , z _ { 1 : k } ) = p ( I _ { k } | I _ { k - 1 } )$ then according to the first-order Markov hypothesis, the unnormalized weight of each particle at time k can be obtained $\mathsf { a s } ,$

$$
w _ { k } ^ { * i } = w _ { k - 1 } ^ { i } p \big ( z _ { k } \big | I _ { k } ^ { i } \big ) = w _ { k - 1 } ^ { i } P \big ( C _ { p m k } , \lambda _ { i } \big ) .\tag{25}
$$

Among them, $C _ { p m }$ is the radiation dose counting rate detected by the detector at time $k , \lambda _ { i }$ is the estimated value of the radiation intensity of the i-th particle at the observation point $\left( x _ { k } , y _ { k } \right)$ The normalized weight of each particle is $\begin{array} { r } { w _ { k } ^ { i } = \frac { w _ { k } ^ { * i } } { \sum _ { j = 1 } ^ { n } w _ { k } ^ { * j } } } \end{array}$ , so we can get a set of weighted particles. Then the estimated values of the radiation source’s parameters are obtained according to Equation (24).

However, in particle filtering, due to frequent resampling, the particles will lack diversity, mainly concentrated on some particles with higher weight. In this paper, a valid number of samples $N _ { t h }$ is set as the threshold. When the weight value $\scriptstyle \sum _ { i = 1 } ^ { n } w _ { k } ^ { i }$ of the current particle set is less than $N _ { t h } ,$ , random resampling is performed by the roulette selection method, and a little noise is added to the particle set after sampling. If without resampling, the particle set is retained directly. In order to improve the diversity of the obtained particle set, the resampled particles are continuously filtered by using the Metropolis–Hastings sampling algorithm [39], so that the sampling points are gradually moved to the central region of the posterior probability distribution. That is, taking $\pmb { I _ { k - 1 } ^ { i } }$ as the mean and $\tau ^ { 2 }$ as the importance sampling function for variance $q \big ( I _ { k } \big | I _ { 0 : k } , z _ { 1 : k } \big )$ , then $q \big ( I _ { k } \big | I _ { 0 : k , z _ { 1 : k } } \big ) = N \big ( I _ { k - 1 } ^ { i } , \tau ^ { 2 } \big )$ . New particle $\pmb { I } _ { 0 : k } ^ { i * }$ is extracted from the importance function $q \big ( I _ { k } \big | I _ { 0 : k } , z _ { 1 : k } \big )$ , and new particles are accepted with a probability value $\begin{array} { r } { \alpha \big ( I _ { 0 : k } ^ { i * } \big ) = \operatorname* { m i n } \biggr \{ 1 , \frac { p ( z _ { 1 : k } | I _ { 0 : k } ^ { i * } ) } { p ( z _ { 1 : k } | I _ { 0 : k } ^ { i } ) } \biggr \} } \end{array}$ until a new particle after the k-th observation is obtained.

## 5. Experimental Analysis and Discussion

## 5.1. Simulation Experiment and Analysis

The simulation preliminarily verified the feasibility of autonomous search of the radioactive source by the robot. The simulation assumptions are as follows:

1. Two-dimensional barrier-free space. The size is 200 m × 200 m;

2. Fixed static radioactive source. $\boldsymbol { I } = \left( 1 4 0 \mathrm { m } , 1 6 0 \mathrm { m } , 0 . 8 5 2 \mathrm { r a d } , 2 . 9 4 \times 1 0 ^ { 8 } \mathrm { B q } \right) ^ { T }$ . The maximum measured value is specified when the robot movement direction $\theta = 0 . 8 5 2$ rad;

Generate count measurements according to Equation (3) and Poisson distribution noise, where En $e r g y n u m b e r = 1 0 0 , \Gamma = 2 . 5 \times 1 0 ^ { - 7 } , w = 1 , f = 3 0 ;$

4. The measured value of environmental background radiation count is 1 cps;

## 5. The calculation method of $P r _ { k }$ refers to the method of [29].

According to the robot’s differential motion model (4), within the duration $\Delta t = 1 s ,$ the robot’s pose at the time $k + 1$ is $\left( x _ { k } , y _ { k } , \theta _ { k } \right)$ , the initial pose of the robot is (30, 20, 0), and the robot’s motion set is A. Combining the factors that affect the positioning accuracy of the radioactive source in Section 3, simulation experiments prove the performance of the algorithm from different schemes.

(1) Algorithm parameters: The number of particles is $n = 5 0 0 0$ , the initialized particle information $x _ { i } , y _ { i }$ are random numbers in the range of [0, 200], and $I _ { i }$ is a random number in the range of $\left\lceil 3 \times 1 0 ^ { 6 } , 1 \times 1 0 ^ { 9 } \right\rceil$ . The robot’s linear velocity $v = 5 \mathrm { m } / \mathrm { s } ,$ angular velocity $\omega = 0 . 1$ rad $/ s$ . Within the duration $\Delta t ,$ the measurement times N are 1, 5, 10, 15, 20 respectively. The condition for the end of the algorithm is that the estimated position error of the radioactive source is less than 1 m $( x \leq 1$ m and $y \le 1  { \mathrm { m } } )$

When $N = 1$ , the simulation results are shown in Figure 2. Figure 2a–d shows the estimated position of the radiation source (represented by green circles), the position of the robot (represented by triangles) and the search trajectory of the robot at time $k = 1 1 , k = 3 0 , k = 4 0 , k = 4 8$ , respectively. When the robot is at the starting point (30, 20), the observation value $z _ { 1 }$ is obtained according to simulation assumption (3) (as shown in Figure $2 \mathrm { e } )$ . Combining the observation value $z _ { 1 }$ and the particle information $( x _ { i } , y _ { i } , I _ { i } )$ , the normalized weight $w _ { 1 } ^ { i }$ of each particle is calculated. The position and size of the radioactive source are estimated by bringing the normalized weight $w _ { 1 } ^ { i }$ and particle information $( x _ { i } , y _ { i } , I _ { i } )$ into formula (24), and the information entropy is further obtained through Equations (21), (22) and (25). The information entropy is used to select the next movement behavior of the robot. Then, the particle information is updated with the effective sample number $N _ { t h } = 2 n / 3 ,$ , position variance $\tau _ { p } ^ { 2 } = 5 0 / i$ , intensity variance $\tau _ { I } ^ { 2 } = 4 . 5 \times 1 0 ^ { 7 } / i$ and acceptance probability $\alpha \big ( I _ { 0 : 1 } ^ { i * } \big )$ . Finally, the algorithm conditions are judged. If the conditions are met, the algorithm is terminated. If the conditions are not met, the robot moves according to the selected behavior, and then observes, until the conditions are met. The simulation results of measurement times $N = 5 , N = 1 0 , N = 1 5 , N = 2 0$ are shown in Figure S1 (Supplemental Materials 1), Figure S2 (Supplemental Materials 2), Figure S3 (Supplemental Materials 3) and Figure S4 (Supplemental Materials 4).

The error statistics of different measurement times within ∆t are shown in Table 1. It can be seen in Table 1 that as the number of measurements increases, the accuracy of the radioactive source intensity estimation is higher. From Figure 2e and Figures S1–S4, it can be found that the greater the number of measurements, the smaller the random error of the observed value. Due to the influence of the robot linear velocity and angular velocity, as the number of measurements increases, the iteration number k decreases to 36 and does not change.

Table 1. Error of radioactive source estimation under different measurement times.
<table><tr><td>Number</td><td>Iterations</td><td>Robot Final Position</td><td>Estimated Source Coordinates</td><td>Error</td><td>Estimated Source Size</td><td>Error</td></tr><tr><td> $N = 1$ </td><td> $k = 4 8$ </td><td>(146.56, 161.06)</td><td>(140.16, 159.99)</td><td>(0.16, 0.01)</td><td> $3 . 1 1 \times 1 0 ^ { 8 }$ </td><td> $1 . 7 4 \times 1 0 ^ { 7 }$ </td></tr><tr><td> $N = 5$ </td><td> $k = 4 2$ </td><td>(142.91, 155.04)</td><td>(140.98, 160.31)</td><td>(0.98, 0.31)</td><td> $2 . 9 7 \times 1 0 ^ { 8 }$ </td><td> $3 . 1 1 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $N = 1 0$ </td><td> $k = 3 8$ </td><td>(137.60, 152.33)</td><td>(139.45, 159.58)</td><td>(0.55, 0.42)</td><td> $2 . 8 6 \times 1 0 ^ { 8 }$ </td><td> $8 . 2 3 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $N = 1 5$ </td><td> $k = 3 7$ </td><td>(135.90, 153.19)</td><td>(139.45, 159.33)</td><td>(0.55, 0.67)</td><td> $2 . 8 9 \times 1 0 ^ { 8 }$ </td><td> $5 . 3 3 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $N = 2 0$ </td><td> $k = 3 7$ </td><td>(135.98, 152.46)</td><td>(139.4, 159.79)</td><td>(0.6, 0.21)</td><td> $2 . 9 0 \times 1 0 ^ { 8 }$ </td><td> $4 . 3 2 \times 1 0 ^ { 6 }$ </td></tr></table>

![](images/5539bc26c37e80ab40b2bc2f793b94b35e5c5e93fe4f7eb04337b224b8b80d6a.jpg)  
(a)

![](images/ac1dab7c8ff417d5b2a195c36eccc87b329013611941338958cc823105007cc0.jpg)  
(b)

![](images/f72f94e535b773814d27cd5fc2b0c88058c0465994390a2066f6be85d9ebddb7.jpg)  
(c)

![](images/eae27897b4356543804610093b16508a18e19168395fdef0a2a65ef6811d20b3.jpg)  
(d)

![](images/f263ef877713d4981d468b704dc5ee093bfc0a12a616f4ccacf17f690b6f18f3.jpg)  
(e)  
Figure 2. The estimation results of radioactive sources when the number of measurements   Figure 2. The estimation results of radioactive sources when the number of measurements $N = 1$    (a) $k = 2 0$ (b)   , (b) $k = 3 0 ,$ (c)   , (c) $k = 4 0 ,$ (d)   (d) $k = 4 8 ,$ In the figure, the blue dot indicates existing particle. In the figure, the blue dot indicates existing particle positions, the green circle indicates the estimated position of the radioactive source, the red circlepositions, the green circle indicates the estimated position of the radioactive source, the red circle indicates the true position of the radioactive source, the red line indicates the robot search path andindicates the true position of the radioactive source, the red line indicates the robot search path and the the red triangle indicates the position of the robot. (e) Shows the measured valred triangle indicates the position of the robot. (e) Shows the measured value $z _ { k }$    obtained duringobtained during the the source seasource search.

(2) Algorithm parameters: The number of particles $n = 5 0 0 0 .$ ferent measurement times., the robot’s linear velocity $v = 5 \mathrm { m } / \mathrm { s } ,$ the angular velocity $\omega = 0 . 1$ rad $/ \mathsf { s } .$ . The number of measurements within ∆t is $N = 2 0$ . The angular Number Iterationvelocity of the robot $\omega = 0 . 1$ rad $/ { \bf s } , \ \omega = 0 . 3$ rad/s, $\omega = 0 . 5$ Errad/s, $\omega = 0 . 7$ rad/s, $\omega = 0 . 9$ rorrad $/ s$ The condition for the end of the algorithm is that the estimated position error of the radioactive source is less than 1 m $( x \leq 1$ m and $\mathrm { y } \leq 1 \mathrm { m } )$ . The simulation results are shown in Figure 3 when $\omega = 0 . 7 \mathrm { r a d } / \mathrm { s }$   = 10   = 38 (137.60, 152.33) (139.45, 159.58) (0.55, 0.42) 2.86 × 108 8.23 × 106The error statistics at different angular velocities are shown in Table 2. As the angular velocity increases,   = 15   = 37 (135.90, 153.19) (139.45, 159.33) (0.55, 0.67) 2.89 × 108 5.33 × 106the number of iterations k decreases first and then increases. It is because as the angular velocity   = 20   = 37 (135.98, 152.46) (139.4, 159.79) (0.6, 0.21) 2.90 × 108 4.32 × 106increases, the robot’s rotation amplitude increases, which affects the observation value and particle weight, thus affecting the robot’s behavior choice. It can be seen from Figure 3a–d and Figures S5–S7 (2) Algorithm parameters: The number of particles   = 5000, the robot’s linear velocity   =(Supplemental Materials 5–7) that as the angular velocity increases, the robot search trajectory shows 5 m/s, the angular an oscillating trend.

lar velocity of the robot   = 0.1 rad/s,   = 0.3 rad/s,   = 0.5 rad/s,   = 0.7 rad/s,   =When the number of measurements and the angular velocity of the robot are constant within the 0.9 rad/duration $\Delta t ,$ he condition for the end of the algorithm is that the estimated position error of the as the robot linear velocity increases during simulation, the number of iterations decreases radioactive source is less than 1 m (x ≤ 1 m and y ≤ 1 m). The simulation results are shown in Figureand the error of the estimated radioactive source remains basically unchanged. However, in the actual 3 when   = 0.7 rad/s. The error statistics at different angular velocprocess, the robot linear velocity increases. Within constant duration $\Delta t ,$ s are shown in Table 2. As the the number of measurements angular velocity increases, the number of iterations   decreases first and then increases. It is becauseshould be gradually reduced. It is because in the actual test process the sensor needs a response as the angular velocity increases, the robot’s rotation amplitude increases, which affects thetime, but the simulation process does not. In addition, when the number of measurements, the linear observation value and particle weight, thus affecting the robot’svelocity and the angular velocity of the robot are constant within $\Delta t ,$ havior choice. It can be seen from the larger the positioning error of Figure 3a–d and Figures S5–S7 (Supplemental Materials 5–7) that as the angular velocity increases, the position sensor, the greater the cumulative position error according to Equation (20). Therefore, the robot search trajectory shows an oscillating trend.the observation value obtained by Equation (3) is smaller, resulting in a larger weight value for each particle, so that the estimated position and size of the radiation source are larger.

![](images/002e42960678c69de6aeaf35a052bb3c4d96781e7c90e1fb59ae28eaa1b63c0d.jpg)  
(a)

![](images/2764b9eeda6a38aa3bf9795c22f639115c1b9f4a3c016f6a18ec439f884ec010.jpg)  
(b)

![](images/f7fad62b35b69f332f5e7e14ab2ab47dd90a1762616e01211a2470b5ff5e51b8.jpg)  
(c)

![](images/e13c1b9048d53de40d9444ba6688d9b884d97cd4baa171d86e8ee4a5c5521d1c.jpg)  
(d)

![](images/128581c2895698dbc1ccd8d22349c6e23f4f0dd671446caedb5a5d525dee0332.jpg)  
(e)  
Figure 3. The estimation results of radioactive sources when the angular velocity $\omega = 0 . 7$ rad/s (a) k = 20, (b) k = 30, (c) k = 33 and (d) k = 40. (e) Shows the measured value $z _ { k }$   obtained during the search of the radioactive source.

Table 2. Errors of radioactive source estimates at different angular velocitieTable 2. Errors of radioactive source estimates at different angular velocities.
<table><tr><td>Angular Velocity</td><td>Iterations</td><td>Robot Final Position</td><td>Estimated Source Coordinates</td><td>Error</td><td>Estimated Source Size</td><td>Error</td></tr><tr><td> $\omega = 0 . 1$ </td><td> $k = 3 7$ </td><td>(135.98, 152.46)</td><td>(139.4, 159.79)</td><td>(0.6, 0.21)</td><td> $2 . 9 0 \times 1 0 ^ { 8 }$ </td><td> $4 . 3 2 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $\omega = 0 . 3$ </td><td> $k = 3 6$ </td><td>(137.34, 151.56)</td><td>(140.89, 159.05)</td><td>(0.89, 0.95)</td><td> $2 . 9 3 \times 1 0 ^ { 8 }$ </td><td> $1 . 3 0 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $\omega = 0 . 5$ </td><td> $k = 3 6$ </td><td>(135.28, 154.00)</td><td>(139.07, 160.19)</td><td>(0.93, 0.19)</td><td> $2 . 8 7 \times 1 0 ^ { 8 }$ </td><td> $7 . 0 3 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $\omega = 0 . 7$ </td><td> $k = 4 0$ </td><td>(138.68, 166.29)</td><td>(139.91, 160.01)</td><td>(0.09, 0.01)</td><td> $2 . 9 2 \times 1 0 ^ { 8 }$ </td><td> $2 . 4 5 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $\omega = 0 . 9$ </td><td> $k = 4 5$ </td><td>(129.91, 167.67)</td><td>(140.33, 159.92)</td><td>(0.33, 0.08)</td><td> $3 . 0 2 \times 1 0 ^ { 8 }$ </td><td> $7 . 9 0 \times 1 0 ^ { 6 }$ </td></tr></table>

## 5.2. Real Experiment and Analysis

When the number of measurements and the angular velocity of the robot are constantTo test the effectiveness of the search algorithm, the experimental design is as follows:

1. The energy of the gamma rays generated when the Cs-137 radioactive source (as shown in Figure 4b), with 37 MBq activity stored in the lead (as shown in Figure 4a), is 0.662 MeV.

m2. surements should be gradually reduced. It is because in the actual test proceThe parameters of the G-M radiation detector are as follows: he sensor need Measurement sponse time, but the simulation process does not. In addition, when the number of measurementsrange—0.01–5000 uSv/h, energy response—40KeV–3 MeV, sensitivity—≥ 3000 cpm/mR/h, linear velocity and the angular velocity of the robot are constant within ∆  , the larger threlative error: ≤15%. The five sides of the cuboid are aluminum alloy shells, and the front panel tioning error of tmaterial is plastic.

E3. ation (20). Therefore, the observation value obtained by Equation (3) is smaller, resulting in Use the TurtleBot robot as the experimental search robot, as shown in Figure 4c. The robot is er weight value for each particle, so that the estimated position and size of the radiation sourcequipped with an Acer notebook, and the notebook is installed with the Ubuntu + ROS system.

a4. larger.The hokuyo UTM-30 lidar sensor is used to establish an environment map in advance, that is, the environment map already exists during the radioactive source search experiment.

5.2. Real Experiment and Analysis5. Obtain the robot’s coordinates by reading the robot’s odometer information.

6. To test the effectiveness of tEquation (1) is simplified as $\begin{array} { r } { \dot { H } = \Upsilon \frac { A } { R ^ { 2 } } } \end{array}$ algorithm, the experimental design is as follows: , and k is constant. The dose equivalent rate measured by the nuclear radiation detector at a distance of 1 m from the radioactive source is 10.45 uSv/h and thus $\Upsilon = 2 . 8 2 4 \times 1 0 ^ { - 8 }$

0.017. According to literature [5], for Cs-137 with an average γ-ray energy of 0.662 MeV, the energy response constant is 12,200 cpm/µSv/h.

8. The position coordinate of the radioactive source in the experiment is $( 6 . 4 \mathrm { m } , 4 . 0 \mathrm { m } , 0 . 5 5 8 6 \mathrm { r a d } )$ the initial position of the robot is (0, 0, 0), and the number of particles is $n = 1 0 0 0$

9. Due to the control of radioactive sources in universities, the experiment is conducted in 12 m × 8 m indoors.

![](images/4d2cedac7a3181aa64ee1c82b78b4b6955e0de9da1befc5df4b811d17029bb3c.jpg)

(a)  
![](images/b8658dfafa59e6f24e133f1514f8381d2ae9b693fd862911aaffdd610e1d825e.jpg)  
(b)

![](images/432e4ce85ae36bea8de0bc768c9c2af9e04eda6dc7914dbf242ad6d171636a32.jpg)  
(c)  
Figure 4. Physical picture of radioactive source and robot system. (a) Lead can. (b) Radioactive source. Figure 4. Physical picture of radioactive source and robot system. (a) Lead can. (b) Radioactive source. (c) Robot system.(c) Robot system.

Combining the factors that affect the positioning accuracy of the radioactive source in Section 3 nd the results of the reference simulation experiments, the angular velocity of the robot in the real and the results of the reference simulation experiments, the angular velocity of the robot in the real xperiment is constant experiment is constant $\omega = 0 . 1 \mathrm { r a d } / \mathrm { s } ;$   the linear velocity of the robot is $v = 0 . 1 \mathrm { m } / \mathrm { s } , v = 0 . 1 5 \mathrm { m } / \mathrm { s } ,$ $v \ = \ 0 . 2 \ : \mathrm { m } / s$ espectively; the number of measurements in the range of duration ∆  =respectively; the number of measurements in the range of duration $\Delta t \ = \ 1 s$ =are $N = 1 , N = 2 , N = 3$ . A total of 9 sets of experiments were conducted. When the estimated position error of the radioactive source satisfies the conditions of $\mathsf { x } \le 0 . 3$ m and $\mathrm { y } \leq 0 . 3$ m each time, the robot he search. The working scene of the robot autonomously searching for the radioactive source is ends the search. The working scene of the robot autonomously searching for the radioactive source is shown in Figure 5a. The trajectory of autonomous search of the robot $( N = 2 , v = 0 . 2 \ : \mathrm { m / s ) }$ is shown in n Figure 5b. The results of the whole experiments are shown in Figure S8 (Supplemental Materials Figure 5b. The results of the whole experiments are shown in Figure S8 (Supplemental Materials 8) ) and the error statistics are shown in Table and the error statistics are shown in Table 3.

It can be seen from Figure S8 and Table 3 that when the number of measurements is constant, the estimated error of the radioactive source coordinates increases with the increase of the robot linear velocity. This is because in nuclear radiation measurements the G-M tube detector has a response time of tens of milliseconds (some G-M tubes even require a response time of a few seconds). When the response time is constant, the greater the linear velocity of the robot, the greater the distance the robot moves during measurement and the greater the positioning error. When the robot linear velocity is constant, the number of measurements increases and the accuracy of estimating the position of the radiation source also increases. Due to the limitation of the detector’s response time, the number of measurements within the duration $\Delta t$ cannot be increased indefinitely. In addition, it can be seen from the experimental results that the method proposed in this paper is not suitable for estimating the activity of radioactive sources.

![](images/e769bdfe5db6379d20f66a4efb8b9e02b16a089ed992cd95c2d1e19292effa38.jpg)  
(a)

![](images/85b94f3e623530c7b470cf99528d6ee9bcd308a5de549469bb484fe2d50d7e89.jpg)  
(b)  
Figure 5. Real experiment. (a) Work scene graph of the robot searching for the radioactive source, (b) Figure 5. Real experiment. (a) Work scene graph of the robot searching for the radioactive source, when  (b) when $N = 2 ,$ 0.2 m/s,   = 0v = 0.2 m/s, $\omega = 0 . 1$ the map and trajectory map of the robot whilerad/s, the map and trajectory map of the robot while automatically searching the radioactive source.automatically searching the radioactive source.

Table 3. Error of radioactive source estimation in the real experiment.
<table><tr><td>Number</td><td>Velocity</td><td>Iterations</td><td>Robot Final Position</td><td>Estimated Source Coordinates</td><td>Error</td><td>Estimated Source Size</td><td>Error</td></tr><tr><td rowspan="3"> $N = 1$ </td><td> $v = 0 . 1$ </td><td> $k = 1 6$ </td><td>(7.25, 2.28)</td><td>(6.24, 4.05)</td><td>(0.16, 0.05)</td><td> $3 . 0 3 \times 1 0 ^ { 7 }$ </td><td> $6 . 7 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $v = 0 . 1 5$ </td><td> $k = 1 5$ </td><td>(6.65, 2.56)</td><td>(6.44, 3.84)</td><td>(0.04, 0.16)</td><td> $3 . 4 7 \times 1 0 ^ { 7 }$ </td><td> $2 . 3 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $v = 0 . 2$ </td><td> $k = 1 5$ </td><td>(6.18, 3.25)</td><td>(6.19, 3.74)</td><td>(0.21, 0.26)</td><td> $2 . 5 3 \times 1 0 ^ { 7 }$ </td><td> $1 . 1 7 \times 1 0 ^ { 7 }$ </td></tr><tr><td rowspan="3"> $N = 2$ </td><td> $v = 0 . 1$ </td><td> $k = 1 3$ </td><td>(5.17, 3.2)</td><td>(6.37, 3.97)</td><td>(0.03, 0.03)</td><td> $3 . 3 1 \times 1 0 ^ { 7 }$ </td><td> $3 . 9 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $v = 0 . 1 5$ </td><td> $k = 1 3$ </td><td>(5.42, 2.77)</td><td>(6.47, 3.94)</td><td>(0.07, 0.06)</td><td> $2 . 9 3 \times 1 0 ^ { 7 }$ </td><td> $7 . 7 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $v = 0 . 2$ </td><td> $k = 1 4$ </td><td>(5.77, 3.14)</td><td>(6.27, 3.87)</td><td>(0.13, 0.13)</td><td> $3 . 0 1 \times 1 0 ^ { 7 }$ </td><td> $6 . 9 \times 1 0 ^ { 6 }$ </td></tr><tr><td rowspan="3"> $N = 3$ </td><td> $v = 0 . 1$ </td><td>k = 12</td><td>(5.29, 2.08)</td><td>(6.42, 4.03)</td><td>(0.02, 0.03)</td><td> $3 . 8 8 \times 1 0 ^ { 7 }$ </td><td> $1 . 8 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $v = 0 . 1 5$ </td><td> $k = 1 2$ </td><td>(5.13, 2.25)</td><td>(6.34, 3.99)</td><td>(0.06, 0.01)</td><td> $3 . 4 4 \times 1 0 ^ { 7 }$ </td><td> $2 . 6 \times 1 0 ^ { 6 }$ </td></tr><tr><td> $v = 0 . 2$ </td><td> $k = 1 2$ </td><td>(4.55, 3.36)</td><td>(6.54, 4.1)</td><td>(0.14, 0.1)</td><td> $2 . 9 7 \times 1 0 ^ { 7 }$ </td><td> $7 . 3 \times 1 0 ^ { 6 }$ </td></tr></table>

## 6. Conclusions

In this paper, a method for autonomous search of radioactive sources by mobile robots was It can be seen from Figure S8 and Table 3 that when the number of measurements is constant, proposed. The next behavior of the robot was chosen through POMDP based on the locally observed the estimated error of the radioactive source coordinates increases with the increase of the robot linearinformation. In the Bayesian framework, the improved MCMC method is used to estimate the velocity. This is because in nuclear radiation measurements the G-M tube detector has a response parameters of the radioactive source, and the robot’s behavior selection is driven by the reward of time of tens of milliseconds (some G-M tubes even require a response time of a few seconds). Wheninformation entropy. In addition, this paper also analyzes the factors that affect the accuracy of the the response time is constant, the greater the linear velocity of the robot, the greater the distance theradiation measurement during the movement of the robot, and designs the behavior set of POMDP robot moves during measurement and the greater the positioning error. When the robot linearaccording to these factors. Simulation and experimental results show that the algorithm has excellent velocity is constant, the number of measurements increases and the accuracy of estimating theperformance in a barrier-free environment. The estimated accuracy of the radioactive source is related position of the radiation source also increases. Due to the limitation of the detector’s response time,to the behavior of the robot, the number of measurements, the accuracy of the position sensor and the number of measurements within the duration ∆  cannot be increased indefinitely. In addition, itthe angle of incidence of the radiation and the sensor. In the future, we will study the autonomous can be seen from the experimental results that the method proposed in this paper is not suitable forsearch of radioactive sources in obstacle environments, and consider the case where there are multiple estimating the activity of radioactive sources.radioactive sources or a coordinated search using multiple land robots or a combination of air and land robots.

Author Contributions: Writing—original draft, data management, review and editing, J.H.; conceptualization, M.L. and K.A.N.; methodology, Y.X., K.A.N. and J.H.; software, H.L., M.G. and J.H.; validation, H.L., M.G. and J.H., project administration, validation, supervision, Y.X.; All authors have read and agreed to the published version of the manuscript.

Funding: This research was funded by theNational Key R&D Program of China (No.2019YFB1310800), China’s 13th Five-Year Plan in the Development of Nuclear Energy (No. 2016(1295)) and Sichuan Science and Technology Program (No. 2019JDRC0141).

Acknowledgments: We would like to thank the National Key Laboratory of Nuclear Waste and Environmental Security of Southwest University of Science and Technology for providing the Cs-137 radioactive source. Thanks to the Engineer Wang Mingsheng for his guidance in the design of the program for the autonomous search of radioactive sources. Thanks to Liu Cheng, Wang Junling and Engineer Du Shigang for their assistance in the real experiments searching for radioactive source.

Conflicts of Interest: The authors declare no conflicts of interest.

## References

1. IAEA Incident and Trafficking Database (ITDB), Incidents of Nuclear and Other Radioactive Material out of Regulatory Control. Available online: https://www.iaea.org/sites/default/files/20/02/itdb-factsheet-2020.pdf (accessed on 13 February 2020).

2. Badhwar, G.D.; Atwell, W.; Badavi, F.F.; Yang, T.C.; Cleghorn, T.F. Space radiation absorbed dose distribution in a human phantom. Radiat. Res. 2002, 157, 76. [CrossRef]

3. Yoshida, T.; Nagatani, K.; Tadokoro, S.; Nishimura, T.; Koyanagi, E. Improvements to the rescue robot quince toward future indoor surveillance missions in the fukushima daiichi nuclear power plant. In Field and Service Robotics; Yoshida, K., Tadokoro, S., Eds.; Springer: Berlin/Heidelberg, Germany, 2014; pp. 19–32.

4. Howse, J.W.; Ticknor, L.O.; Muske, K.R. Least squares estimation techniques for position tracking of radioactive sources. Automatica 2001, 37, 1727–1737. [CrossRef]

Gunatilaka, A.; Ristic, B.; Gailis, R. Radiological Source Localisation. Published by DSTO Defence Science and Technology Organisation, Australia. Available online: http://www.dsto.defence.gov.au/corporate/reports/ DSTO\_TR\_1988.pdf (accessed on 1 July 2007).

6. Rao, N.S.V.; Shankar, M.; Chin, J.C.; Yau, D.K.Y.; Srivathsan, S.; Iyengar, S.S.; Yang, Y.; Hou, J.C. Identification of Low-Level Point Radiation Sources Using a Sensor Network. In Proceedings of the 2008 International Conference on Information Processing in Sensor Networks, St. Louis, MO, USA, 22–24 April 2008; pp. 493–504.

7. Cho, H.S.; Woo, T.H. Mechanical analysis of flying robot for nuclear safety and security control by radiological monitoring. Ann. Nucl. Energy 2016, 94, 138–143. [CrossRef]

8. Morelande, M.; Ristic, B.; Gunatilaka, A. Detection and parameter estimation of multiple radioactive sources. In Proceedings of the 10th International Conference on Information Fusion, Quebec, AB, Canada, 9–12 July 2007; pp. 1–7.

9. Ristic, B.; Gunatilaka, A.; Rutten, M. An information gain driven search for a radioactive point source. In Proceedings of the 10th International Conference on Information Fusion, Quebec, AB, Canada, 9–12 July 2007.

10. Ristic, B.; Gunatilaka, A. Information driven localisation of a radiological point source. Inf. Fusion 2008, 9, 317–326. [CrossRef]

11. Morelande, M.R.; Ristic, B. Radiological Source Detection and Localisation Using Bayesian Techniques. IEEE Trans. Signal Process. 2009, 57, 4220–4423. [CrossRef]

12. Hite, J.; Mattingly, J.; Archer, D.; Willis, M.; Rowe, A.; Bray, K.; Carter, J.; Ghawaly, J. Localization of a radioactive source in an urban environment using Bayesian Metropolis methods. Nucl. Instrum. Methods Phys. Res. A Accel. Spectrom. Detect. Assoc. Equip. 2019, 915, 82–9321. [CrossRef]

13. Meutter, P.D.; Hoffma, I. Bayesian source reconstruction of an anomalous Selenium-75 release at a nuclear research institute. J. Environ. Radioact. 2020, 218, 1062259. [CrossRef]

14. Newaz, A.A.R.; Jeong, S.; Lee, H.; Ryu, H.; Chong, N.Y. UAV-based multiple source localization and contour mapping of radiation fields. Robot. Auton. Syst. 2016, 85, 12–25. [CrossRef]

15. Lee, M. Radiation Source Localization Using a Gamma-ray Camera. Master’s Thesis, Carnegie Mellon University, Pittsburgh, PA, USA, 2018.

16. Klimenko, A.V.; Priedhorsky, W.C.; Hengartner, N.W.; Borozdin, K.N. Efficient strategies for low-statistics nuclear searches. IEEE Trans. Nucl. Sci. 2006, 53, 1435–1442. [CrossRef]

17. Ji, Y.Y.; Lim, T.; Choi, H.Y.; Chung, K.H.; Kang, M.J. Development and Performance of a Multipurpose System for the Environmental Radiation Survey Based on a LaBr3(Ce) Detector. IEEE Trans. Nucl. Sci. 2019, 66, 2422–2429. [CrossRef]

18. Royo, P.; Pastor, E.; Macias, M.; Cuadrado, R.; Barrado, C.; Vargas, A. An Unmanned Aircraft System to Detect a Radiological Point Source Using RIMA Software Architecture. Remote Sens. 2018, 10, 1712. [CrossRef]

19. Li, B.; Zhu, Y.; Wang, Z.; Li, C.; Peng, Z.R.; Ge, L. Use of Multi-Rotor Unmanned Aerial Vehicles for Radioactive Source Search. Remote Sens. 2018, 10, 728. [CrossRef]

20. Cepeda, J.S.; Chaimowicz, L.; Soto, R.; Gordillo, J.L.; Alanís-Reyes, E.A.; Carrillo-Arce, L.C. A Behavior-Based Strategy for Single and Multi-Robot Autonomous Exploration. Sensors 2012, 12, 12772–12797. [CrossRef]

21. Van Nguyen, T.T.; Phung, M.D.; Tran, Q.V. Behavior-based Navigation of Mobile Robot in Unknown Environments Using Fuzzy Logic and Multi-Objective Optimization. Int. J. Control Autom. 2017, 10, 349–364. [CrossRef]

22. Ardiny, H.; Witwicki, S.; Mondada, F. Autonomous Exploration for Radioactive Hotspots Localization Taking Account of Sensor Limitations. Sensors 2019, 19, 292. [CrossRef]

23. Ristic, B.; Morelande, M.; Gunatilaka, A. Information driven search for point sources of gamma radiation. Signal Process. 2010, 90, 1225–1239. [CrossRef]

24. Masson, J.B.; Bailly Bechet, M.; Vergassola, M. Chasing information to search in random Environments. J. Phys. A Math. Theor. 2009, 42, 434009. [CrossRef]

25. Lin, H.I.; Tzeng, H.J. Search strategy of a mobile robot for radiation sources in an unknown environment. In Proceedings of the International Conference on Advanced Robotics and Intelligent Systems (ARIS), Taipei, Taiwan, 6–8 June 2014; pp. 56–60.

26. Lin, H.I.; Tzeng, H.J. Searching a radiological source by a mobile robot. In Proceedings of the International Conference on Fuzzy Theory and Its Applications (iFUZZY), Yilan, Taiwan, 18–20 November 2015; pp. 1–5.

27. Li, J.G.; Cao, M.L.; Meng, Q.H. Chemical Source Searching by Controlling a Wheeled Mobile Robot to Follow an Online Planned Route in Outdoor Field Environments. Sensors 2019, 19, 426. [CrossRef]

28. Monroy, J.; Ruiz-Sarmiento, J.R.; Moreno, F.A.; Melendez-Fernandez, F.; Galindo, C.; Gonzalez-Jimenez, J. A Semantic-Based Gas Source Localization with a Mobile Robot Combining Vision and Chemical Sensing. Sensors 2018, 18, 4174. [CrossRef]

29. Ristic, B.; Skvortsov, A.; Gunatilaka, A. A study of cognitive strategies for an autonomous search. Inf. Fusion 2016, 28, 1–9. [CrossRef]

30. Hutchinson, M.; Oh, H.; Chen, W.H. Entrotaxis as a strategy for autonomous search and source reconstruction in turbulent conditions. Inf. Fusion 2018, 42, 179–189. [CrossRef]

31. Rahbar, F.; Marjovi, A.; Martinoli, A. An Algorithm for Odor Source Localization based on Source Term Estimation. In Proceedings of the International Conference on Robotics and Automation (ICRA), Montreal, QC, Canada, 20–24 May 2019; pp. 973–979.

32. Song, C.; He, Y.; Lei, X. Autonomous Searching for a Diffusive Source Based on Minimizing the Combination of Entropy and Potential Energy. Sensors 2019, 19, 2465. [CrossRef] [PubMed]

33. Bos, A.J.J. Fundamentals of Radiation Dosimetry. In AIP Conference Proceedings; Rosenfeld, A., Kron, T., Errico, F., Moscovitch, M., Eds.; American Institute of Physics: New York, NY, USA, 2011; pp. 5–23.

34. Sullivan, C.J. Radioactive source localization in urban environments with sensor networks and the Internet of Things. In Proceedings of the IEEE International Conference on Multisensor Fusion and Integration for Intelligent Systems (MFI), Baden-Baden, Germany, 19–21 September 2016; pp. 384–388.

35. Shor, Y.B. Statistical methods of analysis and quality control and reliability. In Soviet Radio; Moscow State University: Moscow, Russia, 1962.

36. Majercika, S.M.; Littmanb, M.L. Contingent planning under uncertainty via stochastic satisfiability. Artif. Intell. 2003, 147, 119–162. [CrossRef]

37. Vergassola, M.; Villermaux, E.; Shraiman, B.I. Infotaxis’ as a strategy for searching without gradients. Nature 2007, 445, 406–409. [CrossRef]

38. Silverman, B.W. Density Estimation for Statistical and Data Analysis; Chapman and Hall, CRC Press: Boca Raton, FL, USA, 1986.

39. Gilks, W.R.; Richardson, S.; Spiegelhalter, D. Markov Chain Monte Carlo in Practice; CRC Press: Boca Raton, FL, USA, 1995.

![](images/805c273f09a2ba72e318291856c99ab4bb3c00f4f725800fb2d76fb85ace7909.jpg)

© 2020 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (http://creativecommons.org/licenses/by/4.0/).