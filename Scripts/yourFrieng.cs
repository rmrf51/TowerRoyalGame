using Godot;
using System;
using System.Text;

public class yourFrieng : Sprite
{
	////////////
	string IP_SERVER = "192.168.100.8";//"109.252.37.142";//"127.0.0.1"; //"34.202.96.244"
	int PORT_SERVER = 27000;
	int PORT_CLIENT = 1510;
	PacketPeerUDP socketUDP = new PacketPeerUDP();
	///////////

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
;
	}

//  // Called every frame. 'delta' is the elapsed time since the previous frame.
  public override void _Process(float delta)
  {
	//if (socketUDP.GetAvailablePacketCount() > 0){
	//  	byte[] array_bytes = socketUDP.GetPacket();
	//	GD.Print("msg server: " + Encoding.UTF8.GetString(array_bytes));
	//}
	byte[] array_bytes = socketUDP.GetPacket();
	if(Encoding.UTF8.GetString(array_bytes) != ""){
		GD.Print("Ура, что-то написал");
	}
	
	if(socketUDP.GetAvailablePacketCount() != -1){
	GD.Print("Не равно -1");}
  }
}
