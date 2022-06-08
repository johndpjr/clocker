import argparse

from database import ClockerDatabase
from enums import TaskType, ActionType
import utils


parser = argparse.ArgumentParser(
    description='track your work hours by clocking in and out')

# clock_io_group contains clocking in and out arguments.
#   This group is mutually exclusive b/c one cannot
#   clock in and out at the same time.
clock_io_group = parser.add_mutually_exclusive_group()
clock_io_group.add_argument('-i', '--in', dest='clk_in',
                            action='store_true',
                            help='set action as clocking in')
clock_io_group.add_argument('-o', '--out', dest='clk_out',
                            action='store_true',
                            help='set action as clocking out')

# work_group contains all activities that are being recorded
#   (e.g. work, break, and lunch)
activity_group = parser.add_mutually_exclusive_group()
activity_group.add_argument('-w', '--work', dest='work',
                    action='store_true', help='set task as work')
activity_group.add_argument('-b', '--break', dest='break_',
                    action='store_true', help='set task as break')
activity_group.add_argument('-l', '--lunch', dest='lunch',
                    action='store_true', help='set task as lunch')

# remove_group contains all commands that remove clock records
#   from the table
remove_group = parser.add_mutually_exclusive_group()
remove_group.add_argument('-rm', '--remove',
                    type=int, nargs='+', help='remove the i_th record')
remove_group.add_argument('--clear',
                    action='store_true', help='remove all clock records')

parser.add_argument('-t', '--today',
                    action='store_true', help='display a summary of today\'s work')
parser.add_argument('-d', '--display',
                    action='store_true', help='display work clock records')

args = parser.parse_args()


clockdb = ClockerDatabase()

if (args.work or args.break_ or args.lunch) and (args.clk_in or args.clk_out):
    if args.work:
        clock_type = TaskType.WORK
    elif args.break_:
        clock_type = TaskType.BREAK
    else:
        clock_type = TaskType.LUNCH
    action = ActionType(args.clk_in)

    record = clockdb.add_clk_record(clock_type, action)
    clockdb.display_record(utils.tstr_to_tstamp(record[1]), TaskType(record[2]), ActionType(record[3]))
elif args.remove:
    clockdb.remove_clk_records(args.remove)
elif args.clear:
    clockdb.clear_clk_record()

if args.display and not args.clear:
    clockdb.display()
if args.today:
    clockdb.display_summary_today()
