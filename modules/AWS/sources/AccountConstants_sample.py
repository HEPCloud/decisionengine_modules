{'AWSNOvAAccountConstants':
        {
        'lastKnownBillDate': '06/01/16 00:00', # '%m/%d/%y %H:%M'
        'balanceAtDate': 4210.71,  # $
        'accountName': 'NOvA',
        'accountNumber': 950490332792,
        'credentialsProfileName': 'BillingNOvA',
        'applyDiscount': False, # DLT discount does not apply to credits
        'costRatePerHourInLastSixHoursAlarmThreshold': 2, # $ / h # up to $180/h
        'costRatePerHourInLastDayAlarmThreshold': 2, # $ / h # up to $180/h
        'emailReceipientForAlarms': 'fermilab-cloud-facility-nova@fnal.gov',
        },
 'AWSRnDAccountConstants':
        {
        'lastKnownBillDate': '08/01/16 00:00', # '%m/%d/%y %H:%M'
        'balanceAtDate': 3839.16,    # $
        'accountName': 'RnD',
        'accountNumber': 159067897602,
        'credentialsProfileName':'BillingRnD',
        'applyDiscount': True, # DLT discount does not apply to credits
        'costRatePerHourInLastSixHoursAlarmThreshold': 2, # $ / h # $10/h
        'costRatePerHourInLastDayAlarmThreshold': 2, # $ / h # $10/h
        'emailReceipientForAlarms': 'fermilab-cloud-facility-rnd@fnal.gov'
        },
 'AWSCMSAccountConstants':
        {
        'lastKnownBillDate': '08/01/16 00:00', # '%m/%d/%y %H:%M'
        'balanceAtDate':22324.94,     # $
        'accountName': 'CMS',
        'accountNumber': 486926498429,
        'credentialsProfileName': 'BillingCMS',
        'applyDiscount': True, # DLT discount does not apply to credits
        'costRatePerHourInLastSixHoursAlarmThreshold': 2, # $ / h # up to $1000/h
        'costRatePerHourInLastDayAlarmThreshold': 2, # $ / h # up to $1000/h
        'emailReceipientForAlarms': 'fermilab-cloud-facility-cms@fnal.gov'
        },
 'AWSFermilabAccountConstants':
        {
        'lastKnownBillDate': '08/01/16 00:00', # '%m/%d/%y %H:%M'
        'balanceAtDate': 10690.06,      # $
        'accountName': 'Fermilab',
        'accountNumber': 229161804233,
        'credentialsProfileName': 'BillingFermilab',
        'applyDiscount': True, # DLT discount does not apply to credits
        'costRatePerHourInLastSixHoursAlarmThreshold': 2, # $ / h # $1/h
        'costRatePerHourInLastDayAlarmThreshold': 2, # $ / h # $1/h
        'emailReceipientForAlarms': 'fermilab-cloud-facility-fermilab@fnal.gov'
        },
 'GCEPOCAccountConstants':
        {
        'lastKnownBillDate': '10/01/16 00:00', # '%m/%d/%y %H:%M'
        'balanceAtDate':  6419.55,      # $
        'projectId': 'fermilab-poc', # project_id
        'accountNumber': 750376599029, # NOT CURRENTLY USED
        'credentialsProfileName': None,  # NOT CURRENTLY USERD
        'applyDiscount': False, # Onix does not provide discounts
        'costRatePerHourInLastDayAlarmThreshold': 200, # $ / h # $1/h
        'emailReceipientForAlarms': 'fermilab-cloud-facility-cms@fnal.gov'
        }
 }
