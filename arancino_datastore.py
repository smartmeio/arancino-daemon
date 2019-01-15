import arancino_conf as conf
import redis

class ArancinoDataStore():

    def __init__(self):

        self.__redis_pool_dts = redis.ConnectionPool(host=conf.redis_dts['host'], port=conf.redis_dts['port'], db=conf.redis_dts['db'], decode_responses=conf.redis_dts['dcd_resp'])
        self.__redis_pool_dvs = redis.ConnectionPool(host=conf.redis_dvs['host'], port=conf.redis_dvs['port'], db=conf.redis_dvs['db'], decode_responses=conf.redis_dvs['dcd_resp'])


    def getDataStore(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage data received from the microcontrollers.
        :return:
        """

        #datastore configuration
        #dts_host = conf.redis_dts['host']
        #dts_port = conf.redis_dts['port']
        #dts_db = conf.redis_dts['db']
        #dts_dcd_resp = conf.redis_dts['dcd_resp']

        #__redis_pool_dts = redis.ConnectionPool(host=dts_host, port=dts_port, db=dts_db, decode_responses=dts_dcd_resp)
        return redis.Redis(connection_pool=self.__redis_pool_dts)


    def getDeviceStore(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage configurations of Arancino Devices.
        :return:
        """

        #devicestore configuration
        #dvs_host = conf.redis_dvs['host']
        #dvs_port = conf.redis_dvs['port']
        #dvs_db = conf.redis_dvs['db']
        #dvs_dcd_resp = conf.redis_dvs['dcd_resp']

        #__redis_pool_dvs = redis.ConnectionPool(host=dvs_host, port=dvs_port, db=dvs_db, decode_responses=dvs_dcd_resp)
        return redis.Redis(connection_pool=self.__redis_pool_dvs)
