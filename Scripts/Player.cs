using Godot;
using System;

public class Player : KinematicBody2D
{
	private const float SPEED = 70*4;
	Vector2 movedir = new Vector2(0,0);
	string spritedir = "down";
	
	// Смотрим за нажатиями
	public void controls_loop(){
		var LEFT  = Input.IsActionPressed("ui_left");
		var RIGHT = Input.IsActionPressed("ui_right");
		var UP    = Input.IsActionPressed("ui_up");
		var DOWN  = Input.IsActionPressed("ui_down");
		
		movedir.x = Convert.ToInt32(LEFT) * -1 + Convert.ToInt32(RIGHT);
		movedir.y = Convert.ToInt32(UP) * -1 + Convert.ToInt32(DOWN);	
	}
	
	public void movement_loop(){
		var motion = movedir.Normalized() * SPEED;
		MoveAndSlide(motion, new Vector2(0,0));
	}
	
	public void spritedir_loop(){
		
		if(movedir == new Vector2(-1,0)){
			spritedir = "Left";
		} else if(movedir == new Vector2(1,0)){
			spritedir = "Right";
		} else if(movedir == new Vector2(0,-1)){
			spritedir = "Up";
		} else if(movedir == new Vector2(0,1)){
			spritedir = "Down";
		}
	}
	
	public void anim_switch(string animation){
		var animPlayer = GetNode<AnimationPlayer>("Anim");
		string newanim = animation.ToString() + spritedir;
		
		if(animPlayer.CurrentAnimation != newanim){
			animPlayer.Play(newanim);
		}
	}
	
	public override void _Ready()
	{
		GetViewport().Connect("size_changed", this, "window_resize");
	}
	

	public override void _PhysicsProcess(float delta){
		controls_loop();
		movement_loop();
		spritedir_loop();
		
		if(movedir != new Vector2(0,0)){
			anim_switch("walk");
		} else {
			anim_switch("idle");
		}
		
		//GD.Print(spritedir);
	}

//  // Called every frame. 'delta' is the elapsed time since the previous frame.
//  public override void _Process(float delta)
//  {
//      
//  }
}
