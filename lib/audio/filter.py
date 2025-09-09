import pygame
import pygame.sndarray as sndarray
import numpy as np
from lib.audio.plugin import AudioPlugin


class FilterPlugin(AudioPlugin):
    """
    A versatile audio filter plugin using custom implementations.

    Supports: lowpass, highpass, bandpass, bandstop filters
    without external dependencies beyond numpy.
    """

    FILTER_TYPES = ['lowpass', 'highpass', 'bandpass', 'bandstop']

    def __init__(self, filter_type='lowpass', cutoff_freq=1000, q_factor=0.707,
                 high_cutoff=None):
        """
        Initialize the filter plugin.

        Args:
            filter_type (str): Type of filter ('lowpass', 'highpass', 'bandpass', 'bandstop')
            cutoff_freq (float): Cutoff frequency in Hz (or low cutoff for bandpass/bandstop)
            q_factor (float): Quality factor (0.707 = Butterworth, higher = more resonant)
            high_cutoff (float): High cutoff frequency for bandpass/bandstop filters
        """
        self.filter_type = filter_type.lower()
        self.cutoff_freq = cutoff_freq
        self.high_cutoff = high_cutoff
        self.q_factor = q_factor

        # Filter coefficients (computed when first used)
        self.b = None
        self.a = None
        self.sample_rate = None

        # Filter memory for each channel (biquad sections)
        self.filter_states = {}

        if self.filter_type not in self.FILTER_TYPES:
            raise ValueError(f"Filter type must be one of: {self.FILTER_TYPES}")

    def _design_biquad_coefficients(self):
        """Design biquad filter coefficients using analog prototypes."""
        if self.sample_rate is None:
            self.sample_rate = pygame.mixer.get_init()[0]
            if self.sample_rate is None:
                raise RuntimeError("Pygame mixer not initialized")

        # Normalize frequency
        nyquist = self.sample_rate / 2
        w = 2 * np.pi * self.cutoff_freq / self.sample_rate

        cos_w = np.cos(w)
        sin_w = np.sin(w)
        alpha = sin_w / (2 * self.q_factor)

        if self.filter_type == 'lowpass':
            # Low-pass filter
            b0 = (1 - cos_w) / 2
            b1 = 1 - cos_w
            b2 = (1 - cos_w) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_w
            a2 = 1 - alpha

        elif self.filter_type == 'highpass':
            # High-pass filter
            b0 = (1 + cos_w) / 2
            b1 = -(1 + cos_w)
            b2 = (1 + cos_w) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_w
            a2 = 1 - alpha

        elif self.filter_type == 'bandpass':
            # Band-pass filter (constant skirt gain, peak gain = Q)
            b0 = sin_w / 2
            b1 = 0
            b2 = -sin_w / 2
            a0 = 1 + alpha
            a1 = -2 * cos_w
            a2 = 1 - alpha

        elif self.filter_type == 'bandstop':
            # Band-stop (notch) filter
            b0 = 1
            b1 = -2 * cos_w
            b2 = 1
            a0 = 1 + alpha
            a1 = -2 * cos_w
            a2 = 1 - alpha

        # Normalize coefficients
        self.b = np.array([b0, b1, b2]) / a0
        self.a = np.array([1.0, a1, a2]) / a0

    def _design_multi_stage_filter(self):
        """Design multi-stage filter for bandpass/bandstop using cascaded biquads."""
        if self.filter_type in ['bandpass', 'bandstop'] and self.high_cutoff is not None:
            # Create cascaded filters for better band control
            self.stages = []

            if self.filter_type == 'bandpass':
                # Cascade highpass + lowpass
                # Stage 1: Highpass at low cutoff
                stage1 = FilterPlugin('highpass', self.cutoff_freq, self.q_factor)
                stage1.sample_rate = self.sample_rate
                stage1._design_biquad_coefficients()

                # Stage 2: Lowpass at high cutoff
                stage2 = FilterPlugin('lowpass', self.high_cutoff, self.q_factor)
                stage2.sample_rate = self.sample_rate
                stage2._design_biquad_coefficients()

                self.stages = [stage1, stage2]

            elif self.filter_type == 'bandstop':
                # Parallel lowpass + highpass, then mix
                # Stage 1: Lowpass at low cutoff
                stage1 = FilterPlugin('lowpass', self.cutoff_freq, self.q_factor)
                stage1.sample_rate = self.sample_rate
                stage1._design_biquad_coefficients()

                # Stage 2: Highpass at high cutoff
                stage2 = FilterPlugin('highpass', self.high_cutoff, self.q_factor)
                stage2.sample_rate = self.sample_rate
                stage2._design_biquad_coefficients()

                self.stages = [stage1, stage2]
        else:
            # Single stage filter
            self._design_biquad_coefficients()
            self.stages = None

    def process_sound(self, sound):
        """
        Apply filtering to a Pygame Sound object.

        Args:
            sound (pygame.mixer.Sound): The sound to be processed

        Returns:
            pygame.mixer.Sound: A new, filtered Sound object
        """
        try:
            # Design filter if not already done
            if self.b is None or self.a is None:
                self._design_multi_stage_filter()

            # Convert sound to numpy array
            samples = sndarray.array(sound)

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                # Mono audio
                processed = self._filter_channel(samples, 0)
            else:
                # Stereo audio - process each channel independently
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._filter_channel(samples[:, channel], channel)

            # Convert back to original data type and create new sound
            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Filter processing error: {e}")
            # Return original sound if processing fails
            return sound

    def _filter_channel(self, samples, channel_id):
        """
        Apply biquad filter to a single channel.

        Args:
            samples: Input samples for one channel
            channel_id: Channel identifier for state tracking

        Returns:
            numpy.ndarray: Filtered samples
        """
        if self.stages is not None:
            # Multi-stage filtering
            return self._multi_stage_filter_channel(samples, channel_id)
        else:
            # Single biquad filter
            return self._biquad_filter_channel(samples, channel_id)

    def _biquad_filter_channel(self, samples, channel_id):
        """Apply single biquad filter to channel."""
        # Convert to float for processing
        x = samples.astype(np.float64)
        y = np.zeros_like(x)

        # Initialize or get filter state for this channel
        if channel_id not in self.filter_states:
            self.filter_states[channel_id] = {
                'x': [0.0, 0.0],  # x[n-1], x[n-2]
                'y': [0.0, 0.0]  # y[n-1], y[n-2]
            }

        state = self.filter_states[channel_id]

        # Apply biquad filter: y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
        for n in range(len(x)):
            x_n = x[n]

            y[n] = (self.b[0] * x_n +
                    self.b[1] * state['x'][0] +
                    self.b[2] * state['x'][1] -
                    self.a[1] * state['y'][0] -
                    self.a[2] * state['y'][1])

            # Update state
            state['x'][1] = state['x'][0]
            state['x'][0] = x_n
            state['y'][1] = state['y'][0]
            state['y'][0] = y[n]

        return y

    def _multi_stage_filter_channel(self, samples, channel_id):
        """Apply multi-stage filtering."""
        if self.filter_type == 'bandpass':
            # Cascade: highpass then lowpass
            temp = self.stages[0]._biquad_filter_channel(samples, f"{channel_id}_stage1")
            return self.stages[1]._biquad_filter_channel(temp, f"{channel_id}_stage2")

        elif self.filter_type == 'bandstop':
            # Parallel: lowpass + highpass, then mix
            low = self.stages[0]._biquad_filter_channel(samples, f"{channel_id}_low")
            high = self.stages[1]._biquad_filter_channel(samples, f"{channel_id}_high")
            return (low + high) * 0.5  # Mix with equal weights

        return samples

    def reset_filter_state(self):
        """Reset filter memory."""
        self.filter_states.clear()
        if hasattr(self, 'stages') and self.stages:
            for stage in self.stages:
                stage.reset_filter_state()

    def update_parameters(self, **kwargs):
        """Update filter parameters and force recalculation."""
        if 'filter_type' in kwargs:
            self.filter_type = kwargs['filter_type'].lower()
        if 'cutoff_freq' in kwargs:
            self.cutoff_freq = kwargs['cutoff_freq']
        if 'high_cutoff' in kwargs:
            self.high_cutoff = kwargs['high_cutoff']
        if 'q_factor' in kwargs:
            self.q_factor = kwargs['q_factor']

        # Force recalculation
        self.b = None
        self.a = None
        self.reset_filter_state()


class ResonantFilter(AudioPlugin):
    """
    A resonant filter using state variable filter topology.
    Great for electronic music effects without external dependencies.
    """

    def __init__(self, cutoff_freq=1000, resonance=1.0, filter_type='lowpass'):
        """
        Initialize resonant filter.

        Args:
            cutoff_freq (float): Cutoff frequency in Hz
            resonance (float): Resonance factor (0.1-10.0, 1.0 = no resonance)
            filter_type (str): 'lowpass', 'highpass', or 'bandpass'
        """
        self.cutoff_freq = cutoff_freq
        self.resonance = max(0.1, min(resonance, 10.0))  # Clamp resonance
        self.filter_type = filter_type.lower()

        # Filter state variables for each channel
        self.filter_states = {}

    def process_sound(self, sound):
        """Apply resonant filtering."""
        try:
            samples = sndarray.array(sound)
            sample_rate = pygame.mixer.get_init()[0]

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                processed = self._resonant_filter_channel(samples, 0, sample_rate)
            else:
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._resonant_filter_channel(
                        samples[:, channel], channel, sample_rate
                    )

            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Resonant filter error: {e}")
            return sound

    def _resonant_filter_channel(self, samples, channel_id, sample_rate):
        """Apply state variable filter to channel."""
        # Initialize state variables
        if channel_id not in self.filter_states:
            self.filter_states[channel_id] = {
                'low': 0.0,
                'band': 0.0,
                'high': 0.0
            }

        state = self.filter_states[channel_id]

        # Convert to float
        x = samples.astype(np.float64)
        y = np.zeros_like(x)

        # Calculate filter coefficients
        # Frequency coefficient (0 to 1)
        f = np.clip(2.0 * np.sin(np.pi * self.cutoff_freq / sample_rate), 0.0, 1.0)
        # Resonance coefficient
        q = 1.0 / self.resonance

        # Apply state variable filter
        for i in range(len(x)):
            # State variable filter equations
            state['low'] += f * state['band']
            state['high'] = x[i] - state['low'] - q * state['band']
            state['band'] += f * state['high']

            # Prevent numerical instability
            state['low'] = np.clip(state['low'], -1e6, 1e6)
            state['band'] = np.clip(state['band'], -1e6, 1e6)
            state['high'] = np.clip(state['high'], -1e6, 1e6)

            # Select output
            if self.filter_type == 'lowpass':
                y[i] = state['low']
            elif self.filter_type == 'highpass':
                y[i] = state['high']
            elif self.filter_type == 'bandpass':
                y[i] = state['band']
            else:
                y[i] = x[i]  # Bypass

        return y

    def reset_filter_state(self):
        """Reset filter states."""
        self.filter_states.clear()


class SimpleFilter(AudioPlugin):
    """
    Very simple first-order filters for basic tone shaping.
    Minimal CPU usage, good for real-time applications.
    """

    def __init__(self, filter_type='lowpass', cutoff_freq=1000, mix=1.0):
        """
        Initialize simple filter.

        Args:
            filter_type (str): 'lowpass' or 'highpass'
            cutoff_freq (float): Cutoff frequency in Hz
            mix (float): Dry/wet mix (0.0 = dry, 1.0 = fully filtered)
        """
        self.filter_type = filter_type.lower()
        self.cutoff_freq = cutoff_freq
        self.mix = np.clip(mix, 0.0, 1.0)

        # Filter memory
        self.filter_states = {}

    def process_sound(self, sound):
        """Apply simple filtering."""
        try:
            samples = sndarray.array(sound)
            sample_rate = pygame.mixer.get_init()[0]

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                processed = self._simple_filter_channel(samples, 0, sample_rate)
            else:
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._simple_filter_channel(
                        samples[:, channel], channel, sample_rate
                    )

            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Simple filter error: {e}")
            return sound

    def _simple_filter_channel(self, samples, channel_id, sample_rate):
        """Apply simple first-order filter."""
        if channel_id not in self.filter_states:
            self.filter_states[channel_id] = 0.0

        # Convert to float
        x = samples.astype(np.float64)
        y = np.zeros_like(x)

        # Calculate smoothing coefficient
        rc = 1.0 / (2 * np.pi * self.cutoff_freq)
        dt = 1.0 / sample_rate
        alpha = dt / (rc + dt)

        state = self.filter_states[channel_id]

        for i in range(len(x)):
            if self.filter_type == 'lowpass':
                # Low-pass: smooth the signal
                state = state + alpha * (x[i] - state)
                filtered = state
            else:  # highpass
                # High-pass: input - lowpass
                state = state + alpha * (x[i] - state)
                filtered = x[i] - state

            # Apply mix
            y[i] = (1.0 - self.mix) * x[i] + self.mix * filtered

        self.filter_states[channel_id] = state
        return y

    def reset_filter_state(self):
        """Reset filter state."""
        self.filter_states.clear()


# Preset configurations
class FilterPresets:
    """Predefined filter configurations for common effects."""

    @staticmethod
    def telephone():
        """Classic telephone/radio effect."""
        return FilterPlugin('bandpass', cutoff_freq=300, q_factor=2.0, high_cutoff=3000)

    @staticmethod
    def bass_cut():
        """Remove low frequencies."""
        return FilterPlugin('highpass', cutoff_freq=80, q_factor=0.707)

    @staticmethod
    def treble_cut():
        """Remove high frequencies."""
        return FilterPlugin('lowpass', cutoff_freq=5000, q_factor=0.707)

    @staticmethod
    def notch_60hz():
        """Remove 60Hz hum."""
        return FilterPlugin('bandstop', cutoff_freq=55, q_factor=10.0, high_cutoff=65)

    @staticmethod
    def resonant_sweep():
        """Resonant lowpass for electronic music."""
        return ResonantFilter(cutoff_freq=1000, resonance=5.0, filter_type='lowpass')

    @staticmethod
    def warm_filter():
        """Gentle high-frequency roll-off."""
        return SimpleFilter('lowpass', cutoff_freq=8000, mix=0.5)