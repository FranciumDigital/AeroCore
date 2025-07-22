import time

class PIDController:
    def __init__(self, Kp, Ki, Kd, integrale_limit=None):
        """
        Initialise un contrôleur PID.

        Args:
            Kp (float): Coefficient proportionnel.
            Ki (float): Coefficient intégral.
            Kd (float): Coefficient dérivé.
            integrale_limit (float, optional): Limite anti-windup pour l'intégrale.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integrale_limit = integrale_limit

        self.previous_error = 0
        self.integral = 0

    def compute(self, process_variable, setpoint, dt):
        """
        Calcule la sortie PID.

        Args:
            setpoint (float): Valeur cible.
            process_variable (float): Valeur mesurée.
            dt (float): Temps écoulé depuis le dernier appel (en secondes).

        Returns:
            float: Commande calculée.
        """
        error = setpoint - process_variable

        # Terme proportionnel
        P_out = self.Kp * error

        # Terme intégral
        self.integral += error * dt
        if self.integrale_limit is not None:
            self.integral = max(min(self.integral, self.integrale_limit), -self.integrale_limit)
        I_out = self.Ki * self.integral

        # Terme dérivé
        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0
        D_out = self.Kd * derivative

        # Mémoriser l'erreur pour la prochaine dérivée
        self.previous_error = error

        # Somme des contributions PID
        output = P_out + I_out + D_out
        return output
