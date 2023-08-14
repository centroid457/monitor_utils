# py.con..alerts..monitor.urls

## ENSPIRATION
Suppose you wish to give blood to the Center.
So nowedays you need to make an appointment by websitу, BUT you can't do this while the Center actually don't need your group.
Group necessity shown on Center website and called DonorSvetofor.
And as result you need monitoring it manually, becouse there are no news, email notifications, subscriptions.
It's not difficalt but if you do it as day routine (even once a day) its quite distructing.

So I created it first as Monotor_DonorSvetofor

## Features
1. Threading each monitor
2. monitor data changes in websites
* tag text (regex used)
* tag attribute (regex used)
3. email alert if
* monitored data changed (from last state)
* html structure was changed so parsing can't be finished
* url became unreachable

## IMPORTANT
Now it works as Monotor_DonorSvetofor GBUZ "O.K. Gavrilov DZM Blood Center".  
For each new monitor (URL) you need to create new instance and change settings.

## What do you need to use it as Monotor_DonorSvetofor
1. install python
2. download project
3. apply project requirements
4. add ENVIRONS on your OS for your email account (log/pwd)
5. add script to OS autostart
6. correct your BloodGroup and RH directly in code
7. start script
8. wait email notification
