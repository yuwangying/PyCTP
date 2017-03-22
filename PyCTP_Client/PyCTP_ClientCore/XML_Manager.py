from xml.dom import minidom
from datetime import datetime
import os


class XML_Manager():
    def __init__(self):
        self.__path = "config/bee_config.xml"
        self.__list_user_statistics = list()
        self.__list_arguments = list()
        self.__list_strategy_statistics = list()
        self.__list_position_detail_for_order = list()
        self.__list_position_detail_for_trade = list()
        self.__xml_exist = False  # xml文件是否存在，初始值False
        self.read_xml()
        
    # 读取xml文件
    def read_xml(self):
        # xml文件不存在跳出
        if os.path.exists(self.__path) is False:
            return
        else:
            self.__xml_exist = True

        # 解析文件employ.xml
        self.__doc_read = minidom.parse(self.__path)
        # 定位到根元素
        self.__root_read = self.__doc_read.documentElement

        # 测试代码，开始修改
        self.__path_write_start = "config/bee_config_start.xml"
        NodeList_user_save_info = self.__root_read.getElementsByTagName("user_write_xml_status")
        for i in NodeList_user_save_info:
            dt = datetime.now().strftime('%Y-%m-%d %I:%M:%S')
            i.attributes['datetime'] = dt
        f = open(self.__path_write_start, 'w')
        self.__doc_read.writexml(f, encoding='utf-8')  # addindent='  ', newl='\n',
        f.close()

        self.read_user_save_info()
        self.read_user_instrument_statistics()
        self.read_strategy_arguments()
        self.read_strategy_statistics()
        self.read_position_detail_for_order()
        self.read_position_detail_for_trade()

    # 读期货账户写xml文件状态信息
    def read_user_save_info(self):
        # 期货账户
        NodeList_user_save_info = self.__root_read.getElementsByTagName("user_save_info")
        self.__list_user_save_info = list()
        for i in NodeList_user_save_info:  # i:Element
            dict_user_save_info = dict()
            dict_user_save_info['user_id'] = i.attributes['user_id'].value
            dict_user_save_info['datetime'] = i.attributes['datetime'].value
            dict_user_save_info['tradingday'] = i.attributes['tradingday'].value
            dict_user_save_info['status'] = i.attributes['status'].value
            self.__list_user_save_info.append(dict_user_save_info)

    # 读期货账户下交易合约统计信息
    def read_user_instrument_statistics(self):
        # 期货账户
        NodeList_user_instrument_statistics = self.__root_read.getElementsByTagName("user_instrument_statistics")
        self.__list_user_instrument_statistics = list()
        for i in NodeList_user_instrument_statistics:  # i:Element
            dict_user_statistics = dict()
            dict_user_statistics['user_id'] = i.attributes['user_id'].value
            dict_user_statistics['instrument_id'] = i.attributes['instrument_id'].value
            dict_user_statistics['action_count'] = int(i.attributes['action_count'].value)
            dict_user_statistics['open_count'] = int(i.attributes['open_count'].value)
            self.__list_user_instrument_statistics.append(dict_user_statistics)

    # 读策略参数
    def read_strategy_arguments(self):
        # 策略参数
        NodeList_strategy_arguments = self.__root_read.getElementsByTagName("strategy_arguments")
        self.__list_strategy_arguments = list()
        for i in NodeList_strategy_arguments:
            dict_arguments = dict()
            dict_arguments['user_id'] = i.attributes['user_id'].value
            dict_arguments['strategy_id'] = i.attributes['strategy_id'].value
            dict_arguments['trade_model'] = i.attributes['trade_model'].value
            dict_arguments['order_algorithm'] = i.attributes['strategy_id'].value
            dict_arguments['lots'] = int(i.attributes['lots'].value)
            dict_arguments['lots_batch'] = int(i.attributes['lots_batch'].value)
            dict_arguments['stop_loss'] = int(i.attributes['stop_loss'].value)
            dict_arguments['strategy_on_off'] = int(i.attributes['strategy_on_off'].value)
            dict_arguments['spread_shift'] = int(i.attributes['spread_shift'].value)
            dict_arguments['a_instrument_id'] = i.attributes['a_instrument_id'].value
            dict_arguments['b_instrument_id'] = i.attributes['b_instrument_id'].value
            dict_arguments['a_limit_price_shift'] = int(i.attributes['a_limit_price_shift'].value)
            dict_arguments['b_limit_price_shift'] = int(i.attributes['b_limit_price_shift'].value)
            dict_arguments['a_wait_price_tick'] = int(i.attributes['a_wait_price_tick'].value)
            dict_arguments['b_wait_price_tick'] = int(i.attributes['b_wait_price_tick'].value)
            dict_arguments['a_order_action_limit'] = int(i.attributes['a_order_action_limit'].value)
            dict_arguments['b_order_action_limit'] = int(i.attributes['b_order_action_limit'].value)
            dict_arguments['buy_open'] = float(i.attributes['buy_open'].value)
            dict_arguments['sell_close'] = float(i.attributes['sell_close'].value)
            dict_arguments['sell_open'] = float(i.attributes['sell_open'].value)
            dict_arguments['buy_close'] = float(i.attributes['buy_close'].value)
            dict_arguments['sell_open_on_off'] = int(i.attributes['sell_open_on_off'].value)
            dict_arguments['buy_close_on_off'] = int(i.attributes['buy_close_on_off'].value)
            dict_arguments['buy_open_on_off'] = int(i.attributes['buy_open_on_off'].value)
            dict_arguments['sell_close_on_off'] = int(i.attributes['sell_close_on_off'].value)
            
            dict_arguments['position_a_buy'] = int(i.attributes['position_a_buy'].value)
            dict_arguments['position_a_buy_today'] = int(i.attributes['position_a_buy_today'].value)
            dict_arguments['position_a_buy_yesterday'] = int(i.attributes['position_a_buy_yesterday'].value)
            dict_arguments['position_b_buy'] = int(i.attributes['position_b_buy'].value)
            dict_arguments['position_b_buy_today'] = int(i.attributes['position_b_buy_today'].value)
            dict_arguments['position_b_buy_yesterday'] = int(i.attributes['position_b_buy_yesterday'].value)
            dict_arguments['position_a_sell'] = int(i.attributes['position_a_sell'].value)
            dict_arguments['position_a_sell_today'] = int(i.attributes['position_a_sell_today'].value)
            dict_arguments['position_a_sell_yesterday'] = int(i.attributes['position_a_sell_yesterday'].value)
            dict_arguments['position_b_sell'] = int(i.attributes['position_b_sell'].value)
            dict_arguments['position_b_sell_today'] = int(i.attributes['position_b_sell_today'].value)
            dict_arguments['position_b_sell_yesterday'] = int(i.attributes['position_b_sell_yesterday'].value)
            self.__list_strategy_arguments.append(dict_arguments)
            # print(">>> dict_arguments =", dict_arguments)
            # print(">>> list_arguments =", list_arguments)

    # 读策略统计
    def read_strategy_statistics(self):
        # 策略统计
        NodeList_strategy_statistics = self.__root_read.getElementsByTagName("strategy_statistics")
        self.__list_strategy_statistics = list()
        for i in NodeList_strategy_statistics:
            dict_statistics = dict()
            dict_statistics['user_id'] = i.attributes['user_id'].value
            dict_statistics['strategy_id'] = i.attributes['strategy_id'].value
            dict_statistics['a_order_count'] = int(i.attributes['a_order_count'].value)
            dict_statistics['b_order_count'] = int(i.attributes['b_order_count'].value)
            dict_statistics['a_traded_count'] = int(i.attributes['a_traded_count'].value)
            dict_statistics['b_traded_count'] = int(i.attributes['b_traded_count'].value)
            dict_statistics['total_traded_count'] = int(i.attributes['total_traded_count'].value)
            dict_statistics['a_traded_amount'] = int(i.attributes['a_traded_amount'].value)
            dict_statistics['b_traded_amount'] = int(i.attributes['b_traded_amount'].value)
            dict_statistics['total_traded_amount'] = int(i.attributes['total_traded_amount'].value)
            dict_statistics['a_commission_count'] = float(i.attributes['a_commission_count'].value)
            dict_statistics['b_commission_count'] = float(i.attributes['b_commission_count'].value)
            dict_statistics['commission'] = float(i.attributes['commission'].value)
            dict_statistics['a_trade_rate'] = float(i.attributes['a_trade_rate'].value)
            dict_statistics['b_trade_rate'] = float(i.attributes['b_trade_rate'].value)
            dict_statistics['a_profit_close'] = int(i.attributes['a_profit_close'].value)
            dict_statistics['b_profit_close'] = int(i.attributes['b_profit_close'].value)
            dict_statistics['profit_close'] = int(i.attributes['profit_close'].value)
            dict_statistics['profit'] = float(i.attributes['profit'].value)
            dict_statistics['profit_position'] = float(i.attributes['profit_position'].value)
            dict_statistics['a_action_count'] = int(i.attributes['a_action_count'].value)
            dict_statistics['b_action_count'] = int(i.attributes['b_action_count'].value)
            self.__list_strategy_statistics.append(dict_statistics)

    # 读持仓明细
    def read_position_detail_for_order(self):
        # 交易明细order结构
        NodeList_order = self.__root_read.getElementsByTagName("position_detail_for_order")
        self.__list_position_detail_for_order = list()
        for i in NodeList_order:
            dict_order = dict()
            dict_order['user_id'] = i.attributes['user_id'].value
            dict_order['strategy_id'] = i.attributes['strategy_id'].value
            dict_order['instrumentid'] = i.attributes['instrumentid'].value
            dict_order['orderref'] = i.attributes['orderref'].value
            dict_order['direction'] = i.attributes['direction'].value
            dict_order['comboffsetflag'] = i.attributes['comboffsetflag'].value
            dict_order['combhedgeflag'] = i.attributes['combhedgeflag'].value
            dict_order['limitprice'] = float(i.attributes['limitprice'].value)
            dict_order['volumetotaloriginal'] = int(i.attributes['volumetotaloriginal'].value)
            dict_order['volumetraded'] = int(i.attributes['volumetraded'].value)
            dict_order['volumetotal'] = int(i.attributes['volumetotal'].value)
            dict_order['volumetradedbatch'] = int(i.attributes['volumetradedbatch'].value)
            dict_order['orderstatus'] = i.attributes['orderstatus'].value
            dict_order['tradingday'] = i.attributes['tradingday'].value
            dict_order['tradingdayrecord'] = i.attributes['tradingdayrecord'].value
            dict_order['insertdate'] = i.attributes['insertdate'].value
            dict_order['inserttime'] = i.attributes['inserttime'].value
            self.__list_position_detail_for_order.append(dict_order)
            # print(">>> dict_order =", dict_order)
            # print(">>> self.__list_order =", self.__list_order)

    # 读交易明细
    def read_position_detail_for_trade(self):
        # 交易明细trade结构
        NodeList_trade = self.__root_read.getElementsByTagName("position_detail_for_trade")
        self.__list_position_detail_for_trade = list()
        for i in NodeList_trade:
            dict_trade = dict()
            dict_trade['user_id'] = i.attributes['user_id'].value
            dict_trade['strategy_id'] = i.attributes['strategy_id'].value
            # dict_trade['no'] = i.attributes['no'].value
            dict_trade['instrumentid'] = i.attributes['instrumentid'].value
            dict_trade['orderref'] = i.attributes['orderref'].value
            dict_trade['direction'] = i.attributes['direction'].value
            dict_trade['offsetflag'] = i.attributes['offsetflag'].value
            dict_trade['hedgeflag'] = i.attributes['hedgeflag'].value
            dict_trade['price'] = float(i.attributes['price'].value)
            dict_trade['volume'] = int(i.attributes['volume'].value)
            dict_trade['tradingday'] = i.attributes['tradingday'].value
            dict_trade['tradedate'] = i.attributes['tradedate'].value
            dict_trade['tradingdayrecord'] = i.attributes['tradingdayrecord'].value
            self.__list_position_detail_for_trade.append(dict_trade)
            # print(">>> dict_trade =", dict_trade)
            # print(">>> list_trade =", list_trade)

    # 写入文件xml
    def write_xml(self):
        # 写入xml文件路劲
        self.__path_write = "config/bee_config_end.xml"

        f = open(self.__path_write, 'w')
        self.__dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')
        f.close()

    # 存储xml文件
    def create_xml(self):
        # xml操作入口
        impl = minidom.getDOMImplementation()
        # 创建根
        self.__dom = impl.createDocument(None, "root", None)
        self.__root = self.__dom.documentElement

    # 添加期货账户数据
    def add_user_write_xml_status(self, list_user_write_xml_status):
        for i in list_user_write_xml_status:
            user_write_xml_status = self.__dom.createElement('user')
            user_write_xml_status.attributes['user_id'] = i['user_id']
            dt = datetime.now().strftime('%Y-%m-%d %I:%M:%S')
            user_write_xml_status.attributes['datetime'] = dt
            user_write_xml_status.attributes['tradingday'] = i['tradingday']
            user_write_xml_status.attributes['status'] = i['status']
            self.__root.appendChild(user_write_xml_status)

    # 添加期货账户统计数据
    def add_user_instrument_statistics(self, list_user_instrument_statistics):
        for i in list_user_instrument_statistics:
            # list_user_statisticsy 样本:
            # [{'action_count': 0, 'user_id': '078681', 'instrument_id': 'cu1705', 'open_count': 0},
            #  {'action_count': 0, 'user_id': '078681', 'instrument_id': 'cu1710', 'open_count': 0} ]
            user_instrument_statistics = self.__dom.createElement('user_instrument_statistics')
            user_instrument_statistics.attributes['user_id'] = i['user_id']
            user_instrument_statistics.attributes['instrument_id'] = i['instrument_id']
            user_instrument_statistics.attributes['action_count'] = str(i['action_count'])
            user_instrument_statistics.attributes['open_count'] = str(i['open_count'])
            self.__root.appendChild(user_instrument_statistics)

    # 添加参数数据
    def add_arguments(self, list_argument):
        for i in list_argument:
            arguments = self.__dom.createElement('arguments')
            arguments.attributes['user_id'] = i['user_id']
            arguments.attributes['strategy_id'] = i['strategy_id']
            arguments.attributes['trade_model'] = i['trade_model']
            arguments.attributes['order_algorithm'] = i['strategy_id']
            arguments.attributes['lots'] = str(i['lots'])
            arguments.attributes['lots_batch'] = str(i['lots_batch'])
            arguments.attributes['stop_loss'] = str(i['stop_loss'])
            arguments.attributes['strategy_on_off'] = str(i['strategy_on_off'])
            arguments.attributes['spread_shift'] = str(i['spread_shift'])
            arguments.attributes['a_instrument_id'] = i['a_instrument_id']
            arguments.attributes['b_instrument_id'] = i['b_instrument_id']
            arguments.attributes['a_limit_price_shift'] = str(i['a_limit_price_shift'])
            arguments.attributes['b_limit_price_shift'] = str(i['b_limit_price_shift'])
            arguments.attributes['a_wait_price_tick'] = str(i['a_wait_price_tick'])
            arguments.attributes['b_wait_price_tick'] = str(i['b_wait_price_tick'])
            arguments.attributes['a_order_action_limit'] = str(i['a_order_action_limit'])
            arguments.attributes['b_order_action_limit'] = str(i['b_order_action_limit'])
            arguments.attributes['buy_open'] = str(i['buy_open'])
            arguments.attributes['sell_close'] = str(i['sell_close'])
            arguments.attributes['sell_open'] = str(i['sell_open'])
            arguments.attributes['buy_close'] = str(i['buy_close'])
            arguments.attributes['sell_open_on_off'] = str(i['sell_open_on_off'])
            arguments.attributes['buy_close_on_off'] = str(i['buy_close_on_off'])
            arguments.attributes['buy_open_on_off'] = str(i['buy_open_on_off'])
            arguments.attributes['sell_close_on_off'] = str(i['sell_close_on_off'])

            arguments.attributes['position_a_buy'] = str(i['position_a_buy'])
            arguments.attributes['position_a_buy_today'] = str(i['position_a_buy_today'])
            arguments.attributes['position_b_buy'] = str(i['position_b_buy'])
            arguments.attributes['position_b_buy_today'] = str(i['position_b_buy_today'])
            arguments.attributes['position_a_sell'] = str(i['position_a_sell'])
            arguments.attributes['position_a_sell_today'] = str(i['position_a_sell_today'])
            arguments.attributes['position_a_sell_yesterday'] = str(i['position_a_sell_yesterday'])
            arguments.attributes['position_b_sell'] = str(i['position_b_sell'])
            arguments.attributes['position_b_sell_today'] = str(i['position_b_sell_today'])
            arguments.attributes['position_b_sell_yesterday'] = str(i['position_b_sell_yesterday'])
            self.__root.appendChild(arguments)

    # 添加参数数据
    def add_statistics(self, list_statistics):
        for i in list_statistics:
            statistics = self.__dom.createElement('statistics')
            statistics.attributes['user_id'] = i['user_id']
            statistics.attributes['strategy_id'] = i['strategy_id']
            statistics.attributes['a_order_count'] = str(i['a_order_count'])
            statistics.attributes['b_order_count'] = str(i['b_order_count'])
            statistics.attributes['a_traded_count'] = str(i['a_traded_count'])
            statistics.attributes['b_traded_count'] = str(i['b_traded_count'])
            statistics.attributes['a_traded_amount'] = str(i['a_traded_amount'])
            statistics.attributes['b_traded_amount'] = str(i['b_traded_amount'])
            statistics.attributes['a_commission_count'] = str(i['a_commission_count'])
            statistics.attributes['b_commission_count'] = str(i['b_commission_count'])
            statistics.attributes['a_trade_rate'] = str(i['a_trade_rate'])
            statistics.attributes['b_trade_rate'] = str(i['b_trade_rate'])
            statistics.attributes['a_profit_close'] = str(i['a_profit_close'])
            statistics.attributes['b_profit_close'] = str(i['b_profit_close'])
            statistics.attributes['profit_close'] = str(i['profit_close'])
            statistics.attributes['profit'] = str(i['profit'])
            statistics.attributes['a_action_count'] = str(i['a_action_count'])
            statistics.attributes['b_action_count'] = str(i['b_action_count'])
            self.__root.appendChild(statistics)

    # 添加参数数据
    def add_position_detail_for_order(self, list_order):
        for i in list_order:
            position_detail_for_order = self.__dom.createElement('position_detail_for_order')
            position_detail_for_order.attributes['user_id'] = i['user_id']
            position_detail_for_order.attributes['strategy_id'] = i['strategy_id']
            position_detail_for_order.attributes['instrumentid'] = i['instrumentid']
            position_detail_for_order.attributes['orderref'] = i['orderref']
            position_detail_for_order.attributes['direction'] = i['direction']
            position_detail_for_order.attributes['comboffsetflag'] = i['comboffsetflag']
            position_detail_for_order.attributes['combhedgeflag'] = i['combhedgeflag']
            position_detail_for_order.attributes['limitprice'] = str(i['limitprice'])
            position_detail_for_order.attributes['volumetotaloriginal'] = str(i['volumetotaloriginal'])
            position_detail_for_order.attributes['volumetraded'] = str(i['volumetraded'])
            position_detail_for_order.attributes['volumetotal'] = str(i['volumetotal'])
            position_detail_for_order.attributes['volumetradedbatch'] = str(i['volumetradedbatch'])
            position_detail_for_order.attributes['orderstatus'] = i['orderstatus']
            position_detail_for_order.attributes['tradingday'] = i['tradingday']
            position_detail_for_order.attributes['tradingdayrecord'] = i['tradingdayrecord']
            position_detail_for_order.attributes['insertdate'] = i['insertdate']
            position_detail_for_order.attributes['inserttime'] = i['inserttime']
            self.__root.appendChild(position_detail_for_order)

    # 添加参数数据
    def add_position_detail_for_trade(self, list_trade):
        for i in list_trade:
            position_detail_for_trade = self.__dom.createElement('position_detail_for_trade')
            position_detail_for_trade.attributes['user_id'] = i['user_id']
            position_detail_for_trade.attributes['strategy_id'] = i['strategy_id']
            position_detail_for_trade.attributes['instrumentid'] = i['instrumentid']
            position_detail_for_trade.attributes['orderref'] = i['orderref']
            position_detail_for_trade.attributes['direction'] = i['direction']
            position_detail_for_trade.attributes['offsetflag'] = i['offsetflag']
            position_detail_for_trade.attributes['hedgeflag'] = i['hedgeflag']
            position_detail_for_trade.attributes['price'] = str(i['price'])
            position_detail_for_trade.attributes['volume'] = str(i['volume'])
            position_detail_for_trade.attributes['tradingday'] = i['tradingday']
            position_detail_for_trade.attributes['tradedate'] = i['tradedate']
            position_detail_for_trade.attributes['tradingdayrecord'] = i['tradingdayrecord']
            self.__root.appendChild(position_detail_for_trade)

    def get_xml_exist(self):
        return self.__xml_exist

    def get_list_user_save_info(self):
        return self.__list_user_save_info

    def get_list_user_instrument_statistics(self):
        return self.__list_user_instrument_statistics

    def get_list_strategy_arguments(self):
        return self.__list_strategy_arguments

    def get_list_strategy_statistics(self):
        return self.__list_strategy_statistics

    def get_list_position_detail_for_order(self):
        return self.__list_position_detail_for_order

    def get_list_position_detail_for_trade(self):
        return self.__list_position_detail_for_trade


if __name__ == '__main__':
    xml_manager = XML_Manager()
    # xml_manager.read_xml()
    # list_user = xml_manager.get_list_user_instrument_statistics()
    list_user_instrument_statistics = xml_manager.get_list_user_instrument_statistics()
    list_arguments = xml_manager.get_list_strategy_arguments()
    list_statistics = xml_manager.get_list_strategy_statistics()
    list_order = xml_manager.get_list_position_detail_for_order()
    list_trade = xml_manager.get_list_position_detail_for_trade()
    print(">>> list_user_instrument_statistics =", list_user_instrument_statistics)
    print(">>> list_arguments =", list_arguments)
    print(">>> list_statistics =", list_statistics)
    print(">>> list_order =", list_order)
    print(">>> list_trade =", list_trade)

    xml_manager.create_xml()
    # xml_manager.add_user(list_user)
    xml_manager.add_user_instrument_statistics(list_user_instrument_statistics)
    xml_manager.add_arguments(list_arguments)
    xml_manager.add_statistics(list_statistics)
    xml_manager.add_position_detail_for_order(list_order)
    xml_manager.add_position_detail_for_trade(list_trade)
    xml_manager.add_xml_status()
    xml_manager.write_xml()
