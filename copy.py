class House:
    # 1. We add 'battery' to the setup instructions
    def __init__(self, name, color, battery):
        self.name = name
        self.color = color
        self.battery = battery  # The house now tracks its own battery state permanently!

    def lighton(self):
        print(f"The light in the {self.name} has been turned on...")

    # 2. Because the battery is stored in 'self', we don't need to pass it as an argument here!
    def inverter(self, load):
        # We access the attribute using 'self.battery'
        result = load / self.battery 
        
        if self.battery > 100:
            print(f"[{self.name}] Loading system")
        elif self.battery > 75:
            print(f"[{self.name}] Loading systems...")
        elif self.battery > 50:
            print(f"[{self.name}] Power saving mode...")
        elif self.battery > 25:
            print(f"[{self.name}] Critical warning")
        else:
            print(f"[{self.name}] Shutting down!")

# 3. We define the house's current battery status right at birth
mycity = House("Villa", "Blue", 85)       # Starts with 85% battery
mycity2 = House("Bungalow", "Brown", 12)  # Starts with 12% battery

# 4. Now we only need to tell the inverter what the 'load' is!
mycity.lighton()
mycity.inverter(200)   # Automatically checks 85% -> Prints: [Villa] Loading systems...

print("-" * 20)

mycity2.lighton()
mycity2.inverter(150)  # Automatically checks 12% -> Prints: [Bungalow] Shutting down!
