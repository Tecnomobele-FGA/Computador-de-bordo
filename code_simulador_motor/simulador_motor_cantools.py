import can 
import cantools
from pprint import pprint
db = cantools.database.load_file('BRELETmotor.dbc') # J1939DEMO.dbc')
pprint(db.messages)
message1 = db.get_message_by_name('EVEC1')
message2 = db.get_message_by_name('EVEC2')

pprint (message1.signals)
pprint (message2.signals)

can_bus=can.interface.Bus(bustype='socketcan', channel='can0', bitrate=250000)

data = message1.encode({'EngineSpeed': 520, 'Mileage': 260, 'MotorTorque': 250})
mandou = can.Message(arbitration_id=message1.frame_id, data=data)
can_bus.send(mandou)

data = message2.encode({'Voltage': 300, 'Current': 260, 'Temperature': 50, 
  'Forward':1, 'Backward':1, 'Brake':1, 'Stop':1, 'Ready':1, 
  'IGBT':1, 'OverCurrent':1,'UnderVoltage':1,'OverVoltage':1,'OverHeating':1,
  'OverSpeed':1, 'BMS':1, 'Error75g':1
  })
mandou = can.Message(arbitration_id=message2.frame_id, data=data)
can_bus.send(mandou)


