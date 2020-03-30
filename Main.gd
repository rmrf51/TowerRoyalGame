extends Node2D

export (bool) var debug = false

var realtime_client

func _ready():
	var promise
	
	$NakamaRestClient.connect("completed", self, "_on_NakamaRestClient_completed")

	promise = $NakamaRestClient.authenticate_email("dsnopek@gmail.com", "testing123", true, "dsnopek")
	promise.error == OK and yield(promise, "completed")
	print ("authenticate_email:")
	print (promise.response)

	promise = $NakamaRestClient.get_account()
	promise.error == OK and yield(promise, "completed")
	print ("get_account:")
	print (promise.response)
	var user = promise.response["data"]["user"]
	
	promise = $NakamaRestClient.write_storage_objects([
		{
			collection = "saves",
			key = "save_game",
			value = JSON.print({ progress = 30 }),
		},
		{
			collection = "stats",
			key = "skills",
			value = JSON.print({ skill = 24 }),
		},
	])
	promise.error == OK and yield(promise, "completed")
	print ("write_storage_object:")
	print (promise.response)
	
	promise = $NakamaRestClient.list_storage_objects("saves", user['id'])
	promise.error == OK and yield(promise, "completed")
	print ("list_storage_objects:")
	print (promise.response)
	
	# List a public collection that isn't owned by any user.
	promise = $NakamaRestClient.list_storage_objects("configuration")
	promise.error == OK and yield(promise, "completed")
	print ("list_storage_objects (public):")
	print (promise.response)
	
	realtime_client = $NakamaRestClient.create_realtime_client()
	if not realtime_client:
		print ("Unable to create realtime client")
		return
	yield(realtime_client, "connected")
	
	promise = realtime_client.send({ "status_update": { "status": "heyeo" }})
	promise.error == OK and yield(promise, "completed")
	print ("status_update:")
	print (promise.response)
	
	print ("DONE!")

func _on_NakamaRestClient_completed(response, request):
	if debug:
		print(" ** REQUEST **")
		print(request)
		print(" ** RESPONSE **")
		print(response)

func _process(delta: float) -> void:
	if realtime_client:
		realtime_client.poll()
