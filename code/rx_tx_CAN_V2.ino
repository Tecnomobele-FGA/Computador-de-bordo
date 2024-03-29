///esta dando certo!!!!!!
//Para usar a bibliotecade comunicação SPI
#include <SPI.h>
//Para usar a biblioteca de comunicação CAN
#include <mcp2515.h>
//Pino de entrada que será o CS (Chip Select) da comunicação SPI entre Arduino e o Controlador CAN
MCP2515 mcp2515(10);
//Declara uma estrutura de dados com base numa estrutura predefinida na biblioteca do Controlador CAN
struct can_frame canMsg;
//Declara e inicializa o dado que esse controlador CAN transmitirá
int msgData0 = 0;
#define AD A0    //pino analogico de entrada

void setup()
{
  pinMode(AD, INPUT);
  pinMode(8, OUTPUT);

     
  //Inicia a comunicação Serial
  Serial.begin(9600);
  //Inicia a comunicação SPI
  SPI.begin();
  //Reset do Controlador CAN atraves da SPI do Arduino
  mcp2515.reset();
  //Configura a velocidade de comunicação CAN para 500KBPS com um Clock de 8MHz. Clock do cristal do Controlador MCP2515
  mcp2515.setBitrate(CAN_500KBPS,MCP_8MHZ);
  //Modos de Operação do Controlador CAN: 1. Configuration mode 2. Normal mode 3. Sleep mode 4. Listen-Only mode 5. Loopback mode
  //Configura o modo normal
  mcp2515.setNormalMode();
}

void loop()
{
  int valorAD = analogRead(AD);
  digitalWrite(8, HIGH);
  int tensao = (valorAD*5)/1024;
  Serial.println(valorAD);
 
  // Se houver dado disponivel na Serial para ser lido
  while (Serial.available() > 0)
  {
    msgData0 = Serial.parseInt();
    Serial.println(msgData0);
    // Aguarda um caracter de controle de nova linha (newline)
    if (Serial.read() == '\n');
    canMsg.can_id  = 0x036;               //CAN id = 0x036
    canMsg.can_dlc = 8;                   //CAN data length = 1 (pode ser no máximo 8 bytes)
    canMsg.data[0] = msgData0>>8;            //CAN data0 = 8 primeiros bits (primeiro byte) Dado lido na Serial
    canMsg.data[1] = msgData0;         //Segundo byte
    //canMsg.data[2] = 255;        //Tercerio byte
    //canMsg.data[3] = 255;        //Quarto byte
    canMsg.data[2] = valorAD >> 8;              //CAN data2 = 0
    canMsg.data[3] = valorAD;              //CAN data3 = 0
    //canMsg.data[4] = 0x00;              //CAN data4 = 0
    //canMsg.data[5] = 0x00;              //CAN data5 = 0
    //canMsg.data[6] = 0x00;              //CAN data6 = 0
    //canMsg.data[7] = 255;              //CAN data7 = 0xFF = 255    
    //Enviar a Mensagem CAN - Transceiver colocará essa mensagem no barramento CAN
    mcp2515.sendMessage(&canMsg);
  }
 
  // Lê o dado de uma mensagem específica
  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK)
  {
    if (canMsg.can_id == 0x155)
    {
      int x = canMsg.data[0];              
      Serial.println(x);  
    }else
    Serial.println("nada");
  }
  delay(1000);
}
