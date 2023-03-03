# microchannel-cooling

*COE 347, Senior Design, Spring 2023*

Our project has two main objectives: (1) to create a software program that models the cooling performance of a microchannel cooling system, and (2) to identify an optimal hardware design for microchannel cooling.
For this project, our main deliverable will be a software program which models the thermal performance of a microchannel cooled chip. Optimization will be used to test various designs and layouts of the microchannels and identify an optimal layout. The tool can also be used to dynamically adjust an existing cooling installation to maximize efficiency, i.e. adjust flow rate to raise/lower the dissipated heat flux when the heat produced by the system is higher/lower.  Since the software is modeling the physical system of thermal cooling of a chip, we will have to work within a strict set of hardware limitations set by our research contact.

## Problem Statement

The COOLERCHIPS program is looking to support the development of cooling technologies for current data centers that can scale to the high rack power densities that are predicted in the future. The current method of chip cooling, the cold plate method, is limited by high thermal resistance between the transistors and the cooling system. New high bandwidth memory (HBM) architectures further limit cold plate cooling performance. As a result, a thermal barrier to single-core compute performance exists. It is expected that future cooling systems will need to be scalable for smaller, more modular data centers, making them more feasible. In addition, improved cooling controls could lead to decreased costs by increasing the lifespan of heat-generating components. Additionally, efficient cooling and higher heat rejection temperatures could lead to drastically reduced water consumption and increased potential for future waste heat reuse. Finally, by increasing the efficiency of cooling technologies, the thermal barrier to higher single-core compute performance is removed.

Our team has been asked to research one possible solution, microchannel cooling, and identify an optimal design. We will use a computer model to simulate cooling performance and employ numerical optimization to identify the highest performance design.

## Project Objective

Our project has two main objectives: (1) to create a software program that models the cooling performance of a microchannel cooling system, and (2) to identify an optimal hardware design for microchannel cooling.

Our main deliverable will be a software program which models the thermal performance of a microchannel cooled chip. Optimization will be used to test various designs and layouts of the microchannels and identify an optimal layout. The tool can also be used to dynamically adjust an existing cooling installation to maximize efficiency, i.e. adjust flow rate to raise/lower the dissipated heat flux when the heat produced by the system is higher/lower.  Since the software is modeling the physical system of thermal cooling of a chip, we will have to work within a strict set of hardware limitations set by our research contact.

Our initial model will assume a uniform heat dissipation from the chip and focus on simpler geometries such parallel rectangular channels. Our product will output single values for the total heat flux, backpressure, and output cooling liquid temperature. Optimization will be used to adjust channel and fluid parameters to find the ideal design. If we deliver our minimum requirements early, we will move to the next phase which expands our model using (1) high resolution simulation, (2) non-uniform chip heating, (3) flow and heat transfer visualizations, and (4) more advanced optimization, and more.

## Team Members

* John Matthew Mason, *Team Lead*
* Akhil Sadam, *Technical Lead*
* Shruthi Sundaranand, *Communications Lead*
* Cassandre Korvink
* Cole Nockolds
* Keri Christian
* Long Vu
* Savannah Smith
