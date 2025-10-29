# ESP32-P4-NANO Pinout Reference for ESPHome

**Board:** Waveshare ESP32-P4-NANO
**Chip:** ESP32-P4NRW32
**Note:** This board uses the ESP32-P4 (dual-core RISC-V @ 400MHz) + ESP32-C6 (WiFi 6/BLE 5) co-processor

---

## Quick Reference

### Critical Pin Assignments

**I2C (ES8311 Audio Codec @ 0x18):**
- SDA: GPIO7
- SCL: GPIO8

**I2S Audio (ES8311 Codec):**
- MCLK: GPIO13
- SCLK/BCLK: GPIO12
- LRCK/WS: GPIO10
- ASDOUT (DAC): GPIO11
- DSDIN (ADC/Mic): GPIO9
- PA_Ctrl (Amp Enable): GPIO53

**Ethernet (IP101GRI PHY):**
- TXD[0]: GPIO34, TXD[1]: GPIO35
- RXD[0]: GPIO29, RXD[1]: GPIO30
- TX_EN: GPIO49, CRS_DV: GPIO28
- REF_CLK: GPIO50, MDC: GPIO31
- MDIO: GPIO52, RESET: GPIO51

**SD Card (SDIO 3.0, 4-bit):**
- CLK: GPIO43, CMD: GPIO44
- D0: GPIO39, D1: GPIO40
- D2: GPIO41, D3: GPIO42

**USB Serial/JTAG:**
- D-: GPIO24, D+: GPIO25

**USB OTG:**
- D-: GPIO26, D+: GPIO27

**Display Control (typical):**
- Reset: GPIO27
- Backlight PWM: GPIO26

**Strapping Pins (be careful!):**
- GPIO34, GPIO35, GPIO36, GPIO37, GPIO38

**Free for General Use:**
- GPIO0*, GPIO1*, GPIO2, GPIO3, GPIO4, GPIO5, GPIO6
- GPIO20, GPIO21, GPIO22, GPIO23
- GPIO32, GPIO33, GPIO45, GPIO46, GPIO47, GPIO48
- GPIO54, GPIO83
- *Requires disabling XTAL_32K

---

## MIPI DSI Interface (Display)
The ESP32-P4-NANO has a dedicated 2-lane MIPI DSI connector for displays.

- **Interface:** 2-lane MIPI DSI (D-PHY v1.1, up to 2-lane x 1.5Gbps = 3Gbps total)
- **Connector Type:** MIPI DSI connector
- **Supported Display:** 10.1" capacitive touchscreen (1280×800, 10-point touch)
- **Display Driver Component:** `waveshare/esp_lcd_jd9365_10_1`
- **Common Control Pins:**
  - **Display Reset:** GPIO27 (default, configurable)
  - **Display Backlight PWM:** GPIO26 (default, configurable)

**ESPHome Support:** MIPI DSI is supported in ESPHome as of version 2025.8.0!

**ESPHome Configuration Example:**
```yaml
display:
  - platform: mipi_dsi
    model: CUSTOM  # For the 10.1" display
    dimensions:
      width: 1280
      height: 800
    # Additional configuration based on your specific display
    # See: https://esphome.io/components/display/mipi_dsi/
```

---

## MIPI CSI Interface (Camera)
The ESP32-P4-NANO has a dedicated 2-lane MIPI CSI connector for cameras.

- **Interface:** 2-lane MIPI CSI
- **Connector Type:** MIPI CSI connector
- **Compatible Cameras:** Raspberry Pi cameras
- **Features:** Full HD 1080P acquisition, H.264 encoding
- **Integrated ISP:** Yes (Image Signal Processor)

**ESPHome Note:** MIPI CSI is not currently supported in ESPHome. Use ESP-IDF component directly.

---

## I2C Interface

**Default I2C Pins:**
- **SDA:** GPIO7
- **SCL:** GPIO8

**Connected Devices:**
- **ES8311 Audio Codec** at address `0x18` (used for microphone and speaker)

**Notes:**
- External pullup resistors already present on board
- Do not enable internal pullups in software
- ESP32-P4 has flexible GPIO matrix - any GPIO can be I2C with software configuration

**ESPHome Configuration Example:**
```yaml
i2c:
  sda: GPIO7
  scl: GPIO8
  scan: true
  frequency: 100kHz
```

---

## I2S Interface (Audio)

The board uses the **ES8311** codec chip for audio processing with the **NS4150B** power amplifier.

**I2S Bus Pins (ESP32-P4-NANO):**
- **MCLK (Master Clock):** GPIO13
- **SCLK (Serial Clock/BCLK):** GPIO12
- **LRCK (Left/Right Clock / Word Select):** GPIO10
- **ASDOUT (Audio Serial Data Out to DAC):** GPIO11
- **DSDIN (Digital Serial Data In from ADC):** GPIO9
- **PA_Ctrl (Power Amplifier Enable):** GPIO53 (active high)

**Audio Hardware:**
- **Codec Chip:** ES8311 (mono, low-power)
  - ADC: 24-bit, 8-96 kHz, 100 dB SNR
  - DAC: 24-bit, 8-96 kHz, 110 dB SNR
- **Amplifier:** NS4150B power amplifier chip
- **Microphone:** On-board SMD microphone (connected to ES8311 ADC)
- **Speaker:** MX1.25 2P connector, supports 8Ω 2W speaker

**ES8311 I2C Address:** 0x18

**ESPHome Support:** The ES8311 codec IS fully supported in ESPHome!

**ESPHome Configuration Example:**
```yaml
# I2C for ES8311 control
i2c:
  sda: GPIO7
  scl: GPIO8
  scan: true

# I2S audio bus
i2s_audio:
  - id: i2s_bus
    i2s_lrclk_pin: GPIO10  # LRCK/WS
    i2s_bclk_pin: GPIO12   # SCLK/BCLK

# ES8311 Audio DAC/ADC
audio_dac:
  - platform: es8311
    id: es8311_codec
    bits_per_sample: 16bit
    sample_rate: 16000
    use_mclk: true
    mclk_pin: GPIO13       # Master clock
    use_microphone: true   # Enable microphone input
    mic_gain: 42DB         # Adjust as needed (MIN, 0DB, 6DB, 12DB, 18DB, 24DB, 30DB, 36DB, 42DB, MAX)

# Power amplifier control (optional, enable for speaker output)
output:
  - platform: gpio
    pin: GPIO53
    id: pa_ctrl

# Speaker output
speaker:
  - platform: i2s_audio
    id: my_speaker
    dac_type: external
    i2s_audio_id: i2s_bus
    i2s_dout_pin: GPIO11   # ASDOUT
    audio_dac: es8311_codec
    on_state:
      - output.turn_on: pa_ctrl  # Enable power amplifier when speaking

# Microphone input
microphone:
  - platform: i2s_audio
    id: my_microphone
    adc_type: external
    i2s_audio_id: i2s_bus
    i2s_din_pin: GPIO9     # DSDIN
    audio_dac: es8311_codec
```

---

## Ethernet (RMII Interface)

The ESP32-P4-NANO uses the **IP101GRI** Ethernet PHY chip.

**RMII Interface Pins:**
- **TXD[0]:** GPIO34
- **TXD[1]:** GPIO35
- **TX_EN:** GPIO49
- **RXD[0]:** GPIO29
- **RXD[1]:** GPIO30
- **CRS_DV:** GPIO28 (Carrier Sense/Data Valid)
- **REF_CLK:** GPIO50 (50MHz reference clock from 25MHz crystal)
- **MDIO:** GPIO52 (Management Data I/O)
- **MDC:** GPIO31 (Management Data Clock)
- **PHY_RESET:** GPIO51

**Features:**
- 100Mbps Ethernet
- Optional PoE support (via expansion module)

**ESPHome Configuration Example:**
```yaml
ethernet:
  type: IP101
  mdc_pin: GPIO31
  mdio_pin: GPIO52
  clk_mode: GPIO0_IN
  phy_addr: 0  # Verify actual PHY address
  power_pin: GPIO51  # PHY reset pin
```

**Note:** Verify PHY address and exact clock configuration from Waveshare schematic.

---

## USB Interfaces

### USB Serial/JTAG (Primary)
- **USB D-:** GPIO24 (default)
- **USB D+:** GPIO25 (default)
- **Type:** Full-speed USB Serial/JTAG controller
- **Port:** Type-C UART flashing port

### USB OTG (Full-speed)
- **USB D-:** GPIO26 (default)
- **USB D+:** GPIO27 (default)
- **Type:** Full-speed USB 2.0 OTG with integrated transceiver
- **Port:** Type-A USB 2.0 OTG interface

**Note:** GPIO24/25 and GPIO26/27 can be swapped if only one USB function is needed.

---

## SDIO 3.0 / TF Card Slot

The ESP32-P4-NANO includes a microSD card slot using SDIO 3.0 protocol.

**SDMMC Pins (4-bit mode):**
- **CLK:** GPIO43
- **CMD:** GPIO44
- **D0:** GPIO39
- **D1:** GPIO40
- **D2:** GPIO41
- **D3:** GPIO42

**Features:**
- SDIO 3.0 protocol support
- 4-bit wide bus for high-speed transfers
- Internal pullups available (FLAG_INTERNAL_PULLUP)
- Default frequency: 20 MHz (can be increased to 40 MHz for high-speed mode)

**ESPHome Note:** SD card support in ESPHome is limited. For full SDIO 3.0 functionality, use ESP-IDF directly.

**ESP-IDF Configuration Example:**
```cpp
sdmmc_host_t host = SDMMC_HOST_DEFAULT();
sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();

slot_config.width = 4;  // 4-bit mode
slot_config.clk = 43;
slot_config.cmd = 44;
slot_config.d0 = 39;
slot_config.d1 = 40;
slot_config.d2 = 41;
slot_config.d3 = 42;
slot_config.flags |= SDMMC_SLOT_FLAG_INTERNAL_PULLUP;

// For higher speed (optional)
// host.max_freq_khz = SDMMC_FREQ_HIGHSPEED;  // 40 MHz
```

---

## GPIO Headers

**Form Factor:** 2×13 pin headers (26 pins total per side, 52 pins total)

**Available GPIOs:** 28 programmable GPIOs

### Left Header (J1) - Pin Assignments

| Pin | Function | GPIO | Notes |
|-----|----------|------|-------|
| 1 | SDA | GPIO7 | I2C Data (default) |
| 2 | 3V3 | Power | 3.3V output |
| 3 | SCL | GPIO8 | I2C Clock (default) |
| 4 | 5V | Power | 5V output (USB powered) |
| 5 | TOUCH_CHANNEL_6 | GPIO23 | Touch input / GPIO |
| 6 | 5V | Power | 5V output |
| 7 | TOUCH_CHANNEL_5 | GPIO5 | Touch input / GPIO |
| 8 | GND | Ground | Ground |
| 9 | ADC1_CHANNEL_7 | GPIO20 | ADC input / GPIO |
| 10 | GPIO37 | GPIO37 | UART0_TXD / Strapping pin |
| 11 | ADC1_CHANNEL_4 | GPIO20 | ADC input / GPIO |
| 12 | GPIO38 | GPIO38 | UART0_RXD / Strapping pin |
| 13 | ADC1_CHANNEL_5 | GPIO21 | ADC input / GPIO |
| 14 | GPIO4 | GPIO4 | Touch Channel 2 |
| 15 | TOUCH_CHANNEL_3 | GPIO6 | Touch input / GPIO |
| 16 | GND | Ground | Ground |
| 17 | 3V3 | Power | 3.3V output |
| 18 | GPIO22 | GPIO22 | ADC1 Channel 6 |
| 19 | USB1P1_P0 | GPIO25 | USB Serial/JTAG D- |
| 20 | GND | Ground | Ground |
| 21 | USB1P1_N1 | GPIO26 | USB Serial/JTAG D+ / USB1P1 N0 |
| 22 | GPIO24 | GPIO24 | USB1P1 P1 |
| 23 | GPIO32* | GPIO32 | General purpose |
| 24 | GPIO27 | GPIO27 | USB1P1 P1 |
| 25 | GPIO33 | GPIO33 | General purpose |
| 26 | GND | Ground | Ground |

### Right Header (J2) - Pin Assignments

| Pin | Function | GPIO | Notes |
|-----|----------|------|-------|
| 1 | 5V | Power | 5V output |
| 2 | ESP_LDO_VO4 | Power | LDO output |
| 3 | 3V3 | Power | 3.3V output |
| 4 | GND | Ground | Ground |
| 5 | GND | Ground | Ground |
| 6 | GPIO0 | GPIO0 | XTAL_32K_N (can be GPIO if XTAL disabled) |
| 7 | TOUCH_CHANNEL_1 | GPIO3 | Touch input / GPIO |
| 8 | GPIO1 | GPIO1 | XTAL_32K_P (can be GPIO if XTAL disabled) |
| 9 | TOUCH_CHANNEL_0 | GPIO2 | Touch input / GPIO |
| 10 | GND | Ground | Ground |
| 11 | ADC2_CHANNEL_7 | GPIO54 | ADC input / GPIO |
| 12 | GPIO8 | GPIO8 | TOUCH_CHANNEL_4 / I2C SCL |
| 13 | GPIO47 | GPIO47 | General purpose |
| 14 | GPIO83 | GPIO83 | ADC2 Channel 6 |
| 15 | GPIO46 | GPIO46 | General purpose |
| 16 | GPIO48 | GPIO48 | General purpose |
| 17 | GND | Ground | Ground |
| 18 | GND | Ground | Ground |
| 19 | C6_U0RXD | — | ESP32-C6 UART RX |
| 20 | GPIO45 | GPIO45 | General purpose |
| 21 | C6_IO12 | — | ESP32-C6 GPIO12 |
| 22 | C6_U0TXD | — | ESP32-C6 UART TX |
| 23 | C6_IO13 | — | ESP32-C6 GPIO13 |
| 24 | C6_IO9 | — | ESP32-C6 GPIO9 |
| 25 | GND | Ground | Ground |
| 26 | GND | Ground | Ground |

### Known Reserved/Special Function GPIOs

**Strapping Pins (Boot Configuration):**
- GPIO34 (MTMS) - Ethernet TXD0
- GPIO35 (MTDI) - Ethernet TXD1
- GPIO36 (MTCK) - Strapping only
- GPIO37 (MTDO) - UART0_TXD
- GPIO38 (U0TXD) - UART0_RXD

**I2C (Default):**
- GPIO7 - SDA
- GPIO8 - SCL

**I2S Audio:**
- GPIO9 - DSDIN (ADC data in)
- GPIO10 - LRCK (Word Select)
- GPIO11 - ASDOUT (DAC data out)
- GPIO12 - SCLK (Bit Clock)
- GPIO13 - MCLK (Master Clock)
- GPIO53 - PA_Ctrl (Amplifier enable)

**Ethernet RMII:**
- GPIO28 - CRS_DV
- GPIO29 - RXD0
- GPIO30 - RXD1
- GPIO31 - MDC
- GPIO34 - TXD0
- GPIO35 - TXD1
- GPIO49 - TX_EN
- GPIO50 - REF_CLK
- GPIO51 - PHY_RESET
- GPIO52 - MDIO

**USB Interfaces:**
- GPIO24 - USB Serial/JTAG D- (or USB1P1_P0)
- GPIO25 - USB Serial/JTAG D+ (or USB1P1_N1)
- GPIO26 - USB OTG D- (or USB1P1_N0)
- GPIO27 - USB OTG D+ (or USB1P1_P1)

**SD Card (SDIO 3.0):**
- GPIO39 - D0
- GPIO40 - D1
- GPIO41 - D2
- GPIO42 - D3
- GPIO43 - CLK
- GPIO44 - CMD

**Touch Panel Support:**
- GPIO2 (TOUCH_CHANNEL_0)
- GPIO3 (TOUCH_CHANNEL_1)
- GPIO4 (TOUCH_CHANNEL_2)
- GPIO5 (TOUCH_CHANNEL_5)
- GPIO6 (TOUCH_CHANNEL_3)
- GPIO23 (TOUCH_CHANNEL_6)
- GPIO8 (TOUCH_CHANNEL_4) - shared with I2C SCL

**ADC Channels:**
- GPIO20 (ADC1_CHANNEL_4, ADC1_CHANNEL_7)
- GPIO21 (ADC1_CHANNEL_5)
- GPIO22 (ADC1_CHANNEL_6)
- GPIO54 (ADC2_CHANNEL_7)
- GPIO83 (ADC2_CHANNEL_6)

**ESP32-C6 Co-processor GPIOs (exposed on header):**
- C6_IO9
- C6_IO12
- C6_IO13
- C6_U0RXD (UART RX)
- C6_U0TXD (UART TX)

**Power Pins:**
- **5V:** Available when powered via USB
- **3.3V:** Regulated 3.3V output
- **ESP_LDO_VO4:** LDO voltage output
- **GND:** Ground (multiple pins)

---

## Complete GPIO Allocation Table

Here's a complete overview of all GPIO assignments on the ESP32-P4-NANO:

| GPIO | Primary Function | Secondary/Notes | Available? |
|------|-----------------|-----------------|------------|
| GPIO0 | XTAL_32K_N | Can be GPIO if XTAL disabled | ⚠️ |
| GPIO1 | XTAL_32K_P | Can be GPIO if XTAL disabled | ⚠️ |
| GPIO2 | TOUCH_CHANNEL_0 | Touch input / GPIO | ✓ |
| GPIO3 | TOUCH_CHANNEL_1 | Touch input / GPIO | ✓ |
| GPIO4 | TOUCH_CHANNEL_2 | Touch input / GPIO | ✓ |
| GPIO5 | TOUCH_CHANNEL_5 | Touch input / GPIO | ✓ |
| GPIO6 | TOUCH_CHANNEL_3 | Touch input / GPIO | ✓ |
| GPIO7 | I2C SDA | ES8311 codec @ 0x18 | ⚠️ |
| GPIO8 | I2C SCL / TOUCH_CHANNEL_4 | ES8311 codec | ⚠️ |
| GPIO9 | I2S DSDIN | Microphone ADC input | ✗ |
| GPIO10 | I2S LRCK | Word Select | ✗ |
| GPIO11 | I2S ASDOUT | Speaker DAC output | ✗ |
| GPIO12 | I2S SCLK | Bit Clock | ✗ |
| GPIO13 | I2S MCLK | Master Clock | ✗ |
| GPIO20 | ADC1_CH4/CH7 | ADC input / GPIO | ✓ |
| GPIO21 | ADC1_CH5 | ADC input / GPIO | ✓ |
| GPIO22 | ADC1_CH6 | ADC input / GPIO | ✓ |
| GPIO23 | TOUCH_CHANNEL_6 | Touch input / GPIO | ✓ |
| GPIO24 | USB Serial/JTAG D- | or USB1P1_P0 | ✗ |
| GPIO25 | USB Serial/JTAG D+ | or USB1P1_N1 | ✗ |
| GPIO26 | USB OTG D- | or Display Backlight PWM | ✗ |
| GPIO27 | USB OTG D+ | or Display Reset | ✗ |
| GPIO28 | Ethernet CRS_DV | Carrier Sense | ✗ |
| GPIO29 | Ethernet RXD0 | Receive Data 0 | ✗ |
| GPIO30 | Ethernet RXD1 | Receive Data 1 | ✗ |
| GPIO31 | Ethernet MDC | Management Clock | ✗ |
| GPIO32 | General Purpose | GPIO | ✓ |
| GPIO33 | General Purpose | GPIO | ✓ |
| GPIO34 | Ethernet TXD0 | Strapping pin | ✗ |
| GPIO35 | Ethernet TXD1 | Strapping pin | ✗ |
| GPIO36 | Strapping | Boot config | ✗ |
| GPIO37 | UART0 TXD | Strapping pin | ✗ |
| GPIO38 | UART0 RXD | Strapping pin | ✗ |
| GPIO39 | SD Card D0 | SDIO data | ✗ |
| GPIO40 | SD Card D1 | SDIO data | ✗ |
| GPIO41 | SD Card D2 | SDIO data | ✗ |
| GPIO42 | SD Card D3 | SDIO data | ✗ |
| GPIO43 | SD Card CLK | SDIO clock | ✗ |
| GPIO44 | SD Card CMD | SDIO command | ✗ |
| GPIO45 | General Purpose | GPIO | ✓ |
| GPIO46 | General Purpose | GPIO | ✓ |
| GPIO47 | General Purpose | GPIO | ✓ |
| GPIO48 | General Purpose | GPIO | ✓ |
| GPIO49 | Ethernet TX_EN | Transmit Enable | ✗ |
| GPIO50 | Ethernet REF_CLK | 50MHz Reference | ✗ |
| GPIO51 | Ethernet PHY_RESET | PHY Reset | ✗ |
| GPIO52 | Ethernet MDIO | Management Data | ✗ |
| GPIO53 | PA_Ctrl | Amp Enable | ✗ |
| GPIO54 | ADC2_CH7 | ADC input / GPIO | ✓ |
| GPIO83 | ADC2_CH6 | ADC input / GPIO | ✓ |

**Legend:**
- ✓ = Available for general GPIO use
- ⚠️ = Available but with conditions
- ✗ = Reserved/in use by board peripherals

**Summary:**
- **Total GPIOs exposed on headers:** 52 pins
- **Available for general use:** ~15 GPIOs (GPIO0-6, 20-23, 32-33, 45-48, 54, 83)
- **Reserved for peripherals:** ~37 GPIOs (I2C, I2S, Ethernet, USB, SD Card, etc.)

---

## Document Version

**Document Version:** 2.0
**Last Updated:** October 2025
**Changelog:**
- v2.0: Added complete SD card pinout, corrected ESPHome support status, added comprehensive GPIO allocation table
- v1.0: Initial release

**Source:** Compiled from Waveshare wiki, ESP32-P4 datasheet, pinout diagrams, user-provided schematics, and ESPHome documentation
ources

- **Waveshare Wiki:** https://www.waveshare.com/wiki/ESP32-P4-Nano-StartPage
- **ESP32-P4 Datasheet:** https://www.espressif.com/sites/default/files/documentation/esp32-p4_datasheet_en.pdf
- **ESP-IDF Component Registry:** https://components.espressif.com/
- **10.1" Display Driver:** `waveshare/esp_lcd_jd9365_10_1`

---

## ESPHome Support Summary

**Fully Supported in ESPHome:**
- ✓ MIPI DSI displays (as of ESPHome 2025.8.0)
- ✓ ES8311 audio codec with microphone support
- ✓ I2C sensors (GPIO7/8 or custom pins)
- ✓ Ethernet connectivity (using configuration above)
- ✓ SPI devices
- ✓ UART communication
- ✓ GPIO control (LEDs, relays, switches)
- ✓ ADC sensors

**Currently Limited/Not Supported in ESPHome:**
- ⚠ MIPI CSI cameras (use ESP-IDF)
- ⚠ ESP32-C6 WiFi co-processor (architecture difference - may need ESP-IDF)
- ⚠ SDIO 3.0 SD cards (limited support)

**Best Use Cases:**
- **ESPHome:** Displays, audio/voice, sensors, automation, Ethernet-connected devices
- **ESP-IDF:** Camera applications, complex WiFi co-processor integration, advanced SDIO features

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Source:** Compiled from Waveshare wiki, ESP32-P4 datasheet, and community documentation
