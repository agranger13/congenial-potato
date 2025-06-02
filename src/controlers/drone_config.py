import platform
from kivy.logger import Logger
from jnius import autoclass, cast


class DroneConfig:
    """Classe singleton pour gérer la configuration du drone"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DroneConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ip = "192.168.4.1"
            self.port = "1234"
            self._initialized = True
            self.load_from_preferences()
    
    def load_from_preferences(self):
        """Charge la configuration depuis les SharedPreferences Android"""
        if platform.system() != "Windows":
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                context = cast('android.content.Context', activity)
                
                # Obtenir SharedPreferences
                shared_prefs = context.getSharedPreferences("DroneSettings", 0)
                
                # Charger les valeurs sauvegardées
                self.ip = shared_prefs.getString("drone_ip", self.ip)
                self.port = shared_prefs.getString("drone_port", self.port)
                
                Logger.info(f"Configuration chargée: IP={self.ip}, Port={self.port}")
            except Exception as e:
                Logger.warning(f"Erreur lors du chargement des préférences: {e}")
    
    def save_to_preferences(self):
        """Sauvegarde la configuration dans les SharedPreferences Android"""
        if platform.system() != "Windows":
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                context = cast('android.content.Context', activity)
                
                # Obtenir SharedPreferences
                shared_prefs = context.getSharedPreferences("DroneSettings", 0)
                editor = shared_prefs.edit()
                
                # Sauvegarder les valeurs
                editor.putString("drone_ip", self.ip)
                editor.putString("drone_port", self.port)
                editor.apply()
                
                Logger.info(f"Configuration sauvegardée: IP={self.ip}, Port={self.port}")
            except Exception as e:
                Logger.warning(f"Erreur lors de la sauvegarde des préférences: {e}")
    
    def get_config(self):
        """Retourne la configuration actuelle"""
        return {
            'ip': self.ip,
            'port': self.port
        }
    
    def set_config(self, ip, port):
        """Met à jour la configuration"""
        self.ip = ip
        self.port = port
        self.save_to_preferences()