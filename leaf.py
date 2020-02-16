#!/usr/bin/env python3

from leafpy import Leaf
from configparser import ConfigParser
from datetime import datetime
from argparse import ArgumentParser
import json
import os

debug = True

cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")

def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """
    return (list(name_or_flags), kwargs)

def subcommand(args=[], parent=subparsers):
    """Decorator to define a new subcommand in a sanity-preserving way.
    The function will be stored in the ``func`` variable when the parser
    parses arguments so that it can be called directly like so::
        args = cli.parse_args()
        args.func(args)
    Usage example::
        @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
        def subcommand(args):
            print(args)
    Then on the command line::
        $ python cli.py subcommand -d
    """
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator

@subcommand()
def climateon(args):
    response = leaf.ACRemoteRequest()
    # Wait a few seconds for the request to be made to the car
    # Check status if you don't want to assume it worked:
    leaf.ACRemoteResult(resultKey=response['resultKey'])
    print("Climate control ON.")

@subcommand()
def climateoff(args):
    response = leaf.ACRemoteOffRequest()
    # Wait a few seconds for the request to be made to the car
    # Check status if you don't want to assume it worked:
    leaf.ACRemoteOffResult(resultKey=response['resultKey'])
    print("Climate control OFF.")

@subcommand()
def batteryinfo(args):
    leaf.BatteryStatusCheckRequest()
    # Wait a few seconds for the request to be made to the car
    result = leaf.BatteryStatusRecordsRequest()
    status = (result['BatteryStatusRecords']['PluginState'] + ', ' + result['BatteryStatusRecords']['BatteryStatus']['BatteryChargingStatus'])

    soc = result['BatteryStatusRecords']['BatteryStatus']['SOC']['Value']
    range_nocc = result['BatteryStatusRecords']['CruisingRangeAcOff']
    range_cc = result['BatteryStatusRecords']['CruisingRangeAcOn']
    doneChargingDT = result['BatteryStatusRecords']['TargetDate']

    print('\nCHARGE STATUS:')
    print('Status: ' + status)
    print('SOC: ' + soc + '%')
    print('Charge will finish ' + doneChargingDT)
    print('\nRANGE ESTIMATES (miles):')
    print('Climate control OFF: ' + str(round(int(range_nocc)/(1.61*1000),1)))
    print('Climate control ON: ' + str(round(int(range_cc)/(1.61*1000),1)))

@subcommand()
def energyinfo(args):
    result = leaf.PriceSimulatorDetailInfoRequest()
    month = result['PriceSimulatorDetailInfoResponsePersonalData']['TargetMonth']
    mileage_miles_per_kwh = str(float(result['PriceSimulatorDetailInfoResponsePersonalData']['PriceSimulatorTotalInfo']['TotalElectricMileage'])*1000)
    motor_energy_kwh = result['PriceSimulatorDetailInfoResponsePersonalData']['PriceSimulatorTotalInfo']['TotalPowerConsumptMoter']
    motor_energy_regen_kwh =result['PriceSimulatorDetailInfoResponsePersonalData']['PriceSimulatorTotalInfo']['TotalPowerConsumptMinus']
    motor_energy_net_kwh = result['PriceSimulatorDetailInfoResponsePersonalData']['PriceSimulatorTotalInfo']['TotalPowerConsumptTotal']

    print('\nENERGY INFO for month ' + month)
    print('Mileage (miles/kWh): ' + mileage_miles_per_kwh)
    print('Drive energy to motor (kWh): ' + motor_energy_kwh)
    print('Regen energy from motor (kWh): ' + motor_energy_regen_kwh)
    print('Net energy (kWh): ' + motor_energy_net_kwh)
    print('Energy bill (USD): ' + str(float(config.get('energy','electric_price_dollar_per_kwh'))*float(motor_energy_net_kwh)))

# PARSE ARGUMENTS
if __name__ == "__main__":
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help()
    else:
        # LOG IN
        # Read config file
        config = ConfigParser()
        config.read('config.ini')

        # Did our session with the Nissan API time out? If so go log in again.
        now_ts = datetime.now().timestamp()
        lastLogin_ts = float(config.get('data-internal','last-login-time'))
        if((now_ts - lastLogin_ts)/60) > int(config.get('nissan-api','api-timeout-mins')):
            if debug: print("Logging in, please wait...")
            leaf = Leaf(config.get('nissan-api','username'),config.get('nissan-api','password'))
            if debug: print("Logged in.")

            # save curent session details to config
            config.set('data-internal','last-login-time',str(now_ts))
            config.set('data-internal','session-id', leaf.custom_sessionid)
            config.set('data-internal','session-vin', leaf.VIN)

            with open('config.ini','w') as configfile:
                config.write(configfile)

        else:
            # if we didn't time out, log in using previous session details
            leaf = Leaf(custom_sessionid=config.get('data-internal','session-id'),VIN=config.get('data-internal','session-vin'))

        args.func(args)