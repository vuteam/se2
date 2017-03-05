#ifndef __lcd_h
#define __lcd_h

#include <asm/types.h>
#include <lib/gdi/esize.h>
#include <lib/gdi/erect.h>
#include "gpixmap.h"

#define LCD_CONTRAST_MIN 0
#define LCD_CONTRAST_MAX 63
#define LCD_BRIGHTNESS_MIN 0
#define LCD_BRIGHTNESS_MAX 255

enum op { LED_BRIGHTNESS = 0, LED_DEEPSTANDBY, LED_BLINKINGTIME };

#define LED_IOCTL_BRIGHTNESS_NORMAL 0X10
#define LED_IOCTL_BRIGHTNESS_DEEPSTANDBY 0X11
#define LED_IOCTL_BLINKING_TIME 0X12
#define LED_IOCTL_SET_DEFAULT 0x13

#if defined(__sh__)
#define VFDBRIGHTNESS         0xc0425a03
#define VFDPWRLED             0xc0425a04 /* added by zeroone, also used in fp_control/global.h ; set PowerLed Brightness on HDBOX*/
#define VFDDRIVERINIT         0xc0425a08
#define VFDICONDISPLAYONOFF   0xc0425a0a
#define VFDDISPLAYWRITEONOFF  0xc0425a05
#define VFDDISPLAYCHARS       0xc0425a00

#define VFDCLEARICONS         0xc0425af6
#define VFDSETRF              0xc0425af7
#define VFDSETFAN             0xc0425af8
#define VFDGETWAKEUPMODE      0xc0425af9
#define VFDGETTIME            0xc0425afa
#define VFDSETTIME            0xc0425afb
#define VFDSTANDBY            0xc0425afc
#define VFDREBOOT             0xc0425afd
#define VFDSETLED             0xc0425afe
#define VFDSETMODE            0xc0425aff

#define VFDGETWAKEUPTIME      0xc0425b00
#define VFDGETVERSION         0xc0425b01
#define VFDSETDISPLAYTIME     0xc0425b02
#define VFDSETTIMEMODE        0xc0425b03
#define VFDDISPLAYCLR         0xc0425b00

/* structs are needed for sending icons etc. to aotom                           */
struct set_mode_s {
        int compat; /* 0 = compatibility mode to vfd driver; 1 = nuvoton mode */
};

struct set_brightness_s {
        int level;
};

struct set_icon_s {
        int icon_nr;
        int on;
};

struct set_led_s {
        int led_nr;
        int on;
};

/* time must be given as follows:
 * time[0] & time[1] = mjd ???
 * time[2] = hour
 * time[3] = min
 * time[4] = sec
 */
struct set_standby_s {
        char time[5];
};

struct set_time_s {
        char time[5];
};

struct aotom_ioctl_data {
        union
        {
                struct set_icon_s icon;
                struct set_led_s led;
                struct set_brightness_s brightness;
                struct set_mode_s mode;
                struct set_standby_s standby;
                struct set_time_s time;
        } u;
};
#endif

class eLCD
{
#ifdef SWIG
	eLCD();
	~eLCD();
#else
protected:
	eSize res;
	int lcd_type;
	unsigned char *_buffer;
	int lcdfd;
	int _stride;
	int locked;
	static eLCD *instance;
	void setSize(int xres, int yres, int bpp);
#endif
public:
	static eLCD *getInstance();
	virtual int lock();
	virtual void unlock();
	virtual int islocked() { return locked; };
	virtual bool detected() { return lcdfd >= 0; };
	virtual int setLCDContrast(int contrast)=0;
	virtual int setLCDBrightness(int brightness)=0;
	virtual int setLED(int value, int option)=0;
	virtual void setInverted( unsigned char )=0;
	virtual void setFlipped(bool)=0;
	virtual void setDump(bool)=0;
	virtual int waitVSync()=0;
	virtual bool isOled() const=0;
#if defined(__sh__)
        void ShowIcon(int icon, bool show);
#endif
	int getLcdType() { return lcd_type; };
	virtual void setPalette(gUnmanagedSurface)=0;
#ifndef SWIG
	eLCD();
	virtual ~eLCD();
	uint8_t *buffer() { return (uint8_t*)_buffer; };
	int stride() { return _stride; };
	virtual eSize size() { return res; };
	virtual void update()=0;
#ifdef HAVE_TEXTLCD
	virtual void renderText(ePoint start, const char *text);
#endif
#endif
};

class eDBoxLCD: public eLCD
{
	unsigned char inverted;
	bool flipped;
	bool dump;
#ifdef SWIG
	eDBoxLCD();
	~eDBoxLCD();
#endif
public:
#ifndef SWIG
	eDBoxLCD();
	~eDBoxLCD();
#endif
	int setLCDContrast(int contrast);
	int setLCDBrightness(int brightness);
	int setLED(int value, int option);
	void setInverted( unsigned char );
	void setFlipped(bool);
	void setDump(bool);
	bool isOled() const { return !!lcd_type; };
	void setPalette(gUnmanagedSurface) {};
	void update();
	int waitVSync() { return 0; };
	void dumpLCD2PNG(void);
};

#endif
