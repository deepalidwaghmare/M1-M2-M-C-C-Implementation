import math
import numpy
import random
loop = int(0)

class MyClass():
    def __init__(self, Customer_total, mean_interarrival_Time1, mean_interarrival_Time2, mean_service_Time):
        self.mean_interarrival_FirstClass = mean_interarrival_Time1  # (1/λ1)
        self.mean_interarrival_SecondClass = mean_interarrival_Time2  # (1/λ2)
        self.threshold = 2

        self.mean_service = mean_service_Time
        self.sim_time = 0.0
        self.C_servers = 16
        self.num_event = self.C_servers + 2
        self.num_customers = 0
        self.num_customers_FirstClass = 0
        self.num_customers_SecondClass = 0
        self.num_customers_required = Customer_total

        self.server_status = numpy.zeros(self.C_servers + 1)
        self.area_server_status = numpy.zeros(self.C_servers)
        self.time_next_event = numpy.zeros(self.C_servers + 2)
        self.time_next_event[0] = self.sim_time + self.expon(
            self.mean_interarrival_FirstClass)  # determine next arrival
        self.time_next_event[self.C_servers + 1] = self.sim_time + self.expon(self.mean_interarrival_SecondClass)
        if self.time_next_event[0] < self.time_next_event[self.C_servers + 1]:
            self.next_event_type = 0
        else:
            self.next_event_type = self.C_servers + 1
        for i in range(1, self.C_servers + 1):
            self.time_next_event[i] = math.inf;
        self.server_idle = 0  # determine next departure.
        self.server_utilization = numpy.zeros(self.C_servers)
        self.total_server_utilization = 0
        self.Total_Loss = 0
        self.Total_Loss_FirstClass = 0
        self.Total_Loss_SecondClass = 0




    def timing(self):
        self.min_time_next_event = math.inf
        ##Determine the event type of the next event to occur
        for i in range(0, self.num_event):
            if (self.time_next_event[i] <= self.min_time_next_event):
                self.min_time_next_event = self.time_next_event[i]
                self.next_event_type = i

        self.time_last_event = self.sim_time

        self.sim_time = self.time_next_event[self.next_event_type]  #Simmulation Clock Updated


    def update_time_avg_stats(self):
        self.time_past = self.sim_time - self.time_last_event
        for i in range(1, self.C_servers + 1):
            self.area_server_status[i - 1] += self.time_past * self.server_status[i]


    def arrive_FirstClass(self):
        ix = 0
        self.server_idle = 0
        ##Schedule next arrival
        self.time_next_event[0] = self.sim_time + self.expon(self.mean_interarrival_FirstClass)
        while (self.server_idle == 0 and ix <= self.C_servers):
            if (self.server_status[ix] == 0):
                self.server_idle = ix
            ix += 1
        if (self.server_idle != 0):  ## Someone is IDLE
            self.server_status[self.server_idle] = 1
            self.time_next_event[self.server_idle] = self.sim_time + self.expon(self.mean_service)
        else:  ## server is BUSY
            self.Total_Loss_FirstClass += 1
        self.num_customers_FirstClass += 1

    ############   Define ARRIVE() function (Second Class)

    def arrive_SecondClass(self):
        ix = 0
        self.server_idle = 0
        ##Schedule next arrival
        self.time_next_event[self.C_servers + 1] = self.sim_time + self.expon(self.mean_interarrival_SecondClass)
        while (self.server_idle == 0 and ix <= (self.C_servers - self.threshold)):
            if (self.server_status[ix] == 0):
                self.server_idle = ix
            ix += 1
        if (self.server_idle != 0):  ## Someone is IDLE
            self.server_status[self.server_idle] = 1
            self.time_next_event[self.server_idle] = self.sim_time + self.expon(self.mean_service)
        else:  ## server is BUSY
            self.Total_Loss_SecondClass += 1
        self.num_customers_SecondClass += 1



    def depart(self):
        self.server_status[self.j] = 0
        self.time_next_event[self.j] = math.inf


    def expon(self, mean):
        return (-1 * mean * math.log(random.random()))

    def report(self):
        for i in range(0, self.C_servers):
            self.server_utilization[i] = self.area_server_status[i] / self.sim_time
            self.total_server_utilization += self.area_server_status[i]
        self.total_server_utilization = self.total_server_utilization / (self.sim_time * self.C_servers)
        # print('')
        # print('')
        print('---------Simulation Report-----------')
        # print('')
        µ = 1 / self.mean_service
        λ1 = 1 / self.mean_interarrival_FirstClass
        λ2 = 1 / self.mean_interarrival_SecondClass
        print('λ1 = ', λ1)
        print('λ2 = ', λ2)
        print('µ = ', µ)
        print('')
        print('Total Server Utilization = ', self.total_server_utilization)
        print('Loss Probability of First Class = ', self.Total_Loss_FirstClass / self.num_customers_FirstClass)
        print('')
        print('-------Validation Formula---------')
        Temp1 = 0
        Temp2 = 0
        Temp3 = 0
        for i in range(0, self.C_servers - self.threshold + 1):
            Temp1 += ((1 / math.factorial(i)) * (((λ1 + λ2) / µ) ** i))
        for i in range(self.C_servers - self.threshold + 1, self.C_servers + 1):
            Temp2 += ((1 / (math.factorial(i))) * (((λ1 + λ2) / µ) ** (self.C_servers - self.threshold)) * (
                        (λ1 / µ) ** (i - self.C_servers + self.threshold)))
        P0 = 1 / (Temp1 + Temp2)
        P02 = 1 / (Temp1 + Temp3)

        CBP = self.Total_Loss_SecondClass/self.num_customers_SecondClass
        print('Call Blocking Probability = ', CBP)
        HFP = self.Total_Loss_FirstClass/self.num_customers_FirstClass
        print('Handover Failure Probability = ' , HFP)
        ABP = CBP +(10 * HFP)
        print('Aggregated Blocking Probability = ', ABP)

        #ABP = #Aggregated Blocking Probability (ABP) < 0.02 (Note: if such a value doesn’t exist, state the reason)

        #CBP = #CallBlockingProbability(CBP) = total_new_call_loss / total_new_call_arrivals

        #ABP = #AggregatedBlockingProbability(ABP) = CBP + 10 * HFP


    def main(self):
        while ((self.num_customers_FirstClass + self.num_customers_SecondClass) < self.num_customers_required):
            self.timing()
            self.update_time_avg_stats()
            if (self.next_event_type == 0):
                self.arrive_FirstClass()  ## next event is First Class arrival
            elif (self.next_event_type == (self.C_servers + 1)):
                self.arrive_SecondClass()  ## next event is Second Class arrival
            else:
                self.j = self.next_event_type
                self.depart()  ## next event is departure
        self.report()

myObject = MyClass(Customer_total=300000, mean_interarrival_Time1=34, mean_interarrival_Time2=22, mean_service_Time=100)
myObject.main()