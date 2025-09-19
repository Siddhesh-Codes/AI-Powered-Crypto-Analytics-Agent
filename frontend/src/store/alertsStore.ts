import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import toast from 'react-hot-toast';

export interface Alert {
  id: string;
  symbol: string;
  condition: 'above' | 'below' | 'change_percent';
  value: number;
  message: string;
  enabled: boolean;
  created_at: string;
  triggered: boolean;
}

interface AlertsState {
  alerts: Alert[];
  isLoading: boolean;
  
  // Actions
  createAlert: (alert: Omit<Alert, 'id' | 'created_at' | 'triggered'>) => Promise<void>;
  deleteAlert: (id: string) => Promise<void>;
  toggleAlert: (id: string) => Promise<void>;
  fetchAlerts: () => Promise<void>;
  checkAlerts: (marketData: any[]) => void;
}

export const useAlertsStore = create<AlertsState>()(
  persist(
    (set, get) => ({
      alerts: [],
      isLoading: false,

      createAlert: async (alertData) => {
        set({ isLoading: true });
        
        try {
          const token = localStorage.getItem('token');
          const response = await fetch('http://localhost:8000/api/alerts', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(alertData),
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              set((state) => ({
                alerts: [...state.alerts, data.alert],
                isLoading: false,
              }));
              toast.success('Alert created successfully');
              return;
            }
          }
          
          throw new Error('Failed to create alert');
        } catch (error) {
          console.error('Error creating alert:', error);
          
          // Fallback to local storage
          const newAlert: Alert = {
            ...alertData,
            id: `alert_${Date.now()}`,
            created_at: new Date().toISOString(),
            triggered: false,
          };
          
          set((state) => ({
            alerts: [...state.alerts, newAlert],
            isLoading: false,
          }));
          
          toast.success('Alert created locally');
        }
      },

      deleteAlert: async (id) => {
        try {
          const token = localStorage.getItem('token');
          const response = await fetch(`http://localhost:8000/api/alerts/${id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              set((state) => ({
                alerts: state.alerts.filter(alert => alert.id !== id),
              }));
              toast.success('Alert deleted');
              return;
            }
          }
        } catch (error) {
          console.error('Error deleting alert:', error);
        }

        // Fallback to local deletion
        set((state) => ({
          alerts: state.alerts.filter(alert => alert.id !== id),
        }));
        toast.success('Alert deleted');
      },

      toggleAlert: async (id) => {
        const alert = get().alerts.find(a => a.id === id);
        if (!alert) return;

        try {
          // For now, just update locally since backend doesn't have toggle endpoint
          set((state) => ({
            alerts: state.alerts.map(a => 
              a.id === id ? { ...a, enabled: !a.enabled } : a
            ),
          }));
          
          toast.success(`Alert ${alert.enabled ? 'disabled' : 'enabled'}`);
        } catch (error) {
          console.error('Error toggling alert:', error);
          toast.error('Failed to update alert');
        }
      },

      fetchAlerts: async () => {
        set({ isLoading: true });
        
        try {
          const token = localStorage.getItem('token');
          const response = await fetch('http://localhost:8000/api/alerts', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              set({
                alerts: data.alerts,
                isLoading: false,
              });
              return;
            }
          }
        } catch (error) {
          console.error('Error fetching alerts:', error);
        }
        
        set({ isLoading: false });
      },

      checkAlerts: (marketData) => {
        const { alerts } = get();
        const activeAlerts = alerts.filter(alert => alert.enabled && !alert.triggered);
        
        activeAlerts.forEach(alert => {
          const crypto = marketData.find(c => c.symbol === alert.symbol);
          if (!crypto) return;
          
          let triggered = false;
          
          switch (alert.condition) {
            case 'above':
              triggered = crypto.price > alert.value;
              break;
            case 'below':
              triggered = crypto.price < alert.value;
              break;
            case 'change_percent':
              triggered = Math.abs(crypto.priceChangePercent24h) >= alert.value;
              break;
          }
          
          if (triggered) {
            // Mark as triggered
            set((state) => ({
              alerts: state.alerts.map(a => 
                a.id === alert.id ? { ...a, triggered: true } : a
              ),
            }));
            
            // Show notification
            toast.success(
              `🚨 Alert: ${alert.message || `${alert.symbol} ${alert.condition} ${alert.value}`}`,
              { duration: 8000 }
            );
          }
        });
      },
    }),
    {
      name: 'alerts-storage',
      partialize: (state) => ({
        alerts: state.alerts,
      }),
    }
  )
);
