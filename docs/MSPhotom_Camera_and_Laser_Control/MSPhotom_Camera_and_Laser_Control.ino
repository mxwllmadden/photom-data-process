#define DEBUG 0 // change to 1 to debug 

// IMPORTANT NOTE: Arduino internal clocks are not guarenteed to be accurate over long periods of time!!!!
// If you are aligning to behavior or events collected by a seperate system, you SHOULD NOT rely on arduino timing to be accurate
// To combat this we keep trial length low and repeatedly trigger new trials from the 'controlling' behavior computer/device. This prevents
// accumulation of drift over long sessions.

const int outStim1 = 7; // Output pin for Laser 1 activation
const int outStim2 = 12; // Output pin for Laser 2 activation
const int BoxIn = 2; // Input pin from behavior system, triggers 
const int CamTrigger = 4; // Output pin to trigger camera shutter/aquisition
const int ImgPerActivation = 300; // Number of images to capture per channel per trigger event. This is equivalent to 'Images per channel per trial'. At 10hz aquisition rate, this is the number of deciseconds per trial.
int BoxTTL = 0; // Variable to store input TTL pulse values (triggers).
int camCtrl = 0; // Default value of zero; 0 indicates camera should be activated if trigger is received, 1 disables camera aquisition.

void setup() {
  if(DEBUG) {
   // initialize serial communication at 9600 bits per second (to write debugging info back to terminal)
    Serial.begin(9600); 
  }
  // set pin modes
  pinMode(outStim1, OUTPUT);
  pinMode(outStim2, OUTPUT);
  pinMode(BoxIn, INPUT);
  pinMode(CamTrigger, OUTPUT);
 }
 
 void loop() {
   BoxTTL = digitalRead(BoxIn); //Note that "on" for MedAssociates TTL output is 0 and "off" is 1
 
 if(BoxTTL == 0) // When trigger is received
    {
      if (camCtrl == 0) // If camera control is on
      {
        for (int x = 0; x < ImgPerActivation ; x++){ // Record 1 trial's worth of images
        digitalWrite(LED_BUILTIN, HIGH); // Turn on board led
        digitalWrite(outStim1, HIGH); // Turn on Laser 1
        digitalWrite(outStim2, LOW); // Turn off Laser 2
        digitalWrite(CamTrigger, HIGH); // Turn on Camera Trigger
        delay(5); // Wait 5ms
        digitalWrite(CamTrigger, LOW); // Turn off Camera Trigger
  
        delay(40); // wait 40ms
        digitalWrite(outStim1, LOW); // Turn off Laser 1
        digitalWrite(LED_BUILTIN, LOW); // Turn off board led
        delay(5); // wait 5ms
        
        digitalWrite(outStim2, HIGH); // Turn on Laser 2
        digitalWrite(CamTrigger, HIGH); // Turn on Camera
        delay(5); // Wait 5ms
        digitalWrite(CamTrigger, LOW); // Turn off Camera Trigger
  
        delay(40); // Wait 40ms
        digitalWrite(outStim2, LOW); // Turn off Laser 2
     
        delay(5); // Wait 5ms, this brings the total time for each loop to 100 ms for 10hz data collection
        }
        camCtrl = 1; // When the loop is done, turn off camera output, this is to protect from continuous trial triggering 
      }
      else if (camCtrl == 1) // This triggers if the BoxIn TTL remains on while 
      { // Same loop as above but without camera triggers
        digitalWrite(outStim1, HIGH);
        digitalWrite(outStim2, LOW);
        delay(45);
        digitalWrite(outStim1, LOW);       
        delay(5);

        digitalWrite(outStim2, HIGH);
        delay(45);
        digitalWrite(outStim2, LOW);
        delay(5);        
      }
    }
    else if(BoxTTL == 1) // Keep lasers off when no TTL Pulse is received and make the board ready for new input (reset CamCtrl)
    {
     digitalWrite(outStim1, LOW); 
     digitalWrite(outStim2, LOW);
     digitalWrite(CamTrigger, LOW);
     camCtrl = 0;
    }
 }
