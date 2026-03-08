import { useState } from "react";
import {
  Settings as SettingsIcon, Globe, Bell, Mail, Share2, Bot,
  CalendarClock, Save, CheckCircle2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

interface SettingsState {
  eventName: string;
  eventDate: string;
  eventLocation: string;
  eventDescription: string;
  emailProvider: string;
  emailFromName: string;
  emailReplyTo: string;
  emailDailyLimit: string;
  twitterEnabled: boolean;
  twitterHandle: string;
  linkedinEnabled: boolean;
  linkedinPage: string;
  instagramEnabled: boolean;
  instagramHandle: string;
  notifyEmail: boolean;
  notifyScheduleChanges: boolean;
  notifyCrisisAlerts: boolean;
  notifyAgentErrors: boolean;
  notifyRegistrations: boolean;
  notifyDigestFrequency: string;
  automationLevel: number[];
  autoSchedule: boolean;
  autoEmail: boolean;
  autoSocial: boolean;
  autoCrisis: boolean;
  agentConcurrency: string;
}

const SettingsPage = () => {
  const { toast } = useToast();
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState<SettingsState>({
    eventName: "TechSummit 2026",
    eventDate: "2026-03-15",
    eventLocation: "San Francisco, CA",
    eventDescription: "A 3-day conference bringing together 2000+ developers, engineers, and tech leaders.",
    emailProvider: "lovable",
    emailFromName: "TechSummit Team",
    emailReplyTo: "hello@techsummit.dev",
    emailDailyLimit: "500",
    twitterEnabled: true,
    twitterHandle: "@techsummit2026",
    linkedinEnabled: true,
    linkedinPage: "techsummit-conference",
    instagramEnabled: true,
    instagramHandle: "@techsummit2026",
    notifyEmail: true,
    notifyScheduleChanges: true,
    notifyCrisisAlerts: true,
    notifyAgentErrors: true,
    notifyRegistrations: false,
    notifyDigestFrequency: "daily",
    automationLevel: [75],
    autoSchedule: true,
    autoEmail: true,
    autoSocial: true,
    autoCrisis: true,
    agentConcurrency: "4",
  });

  const update = <K extends keyof SettingsState>(key: K, value: SettingsState[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSave = () => {
    // Persist to localStorage for now
    localStorage.setItem("swarm_settings", JSON.stringify(settings));
    setSaved(true);
    toast({ title: "Settings saved", description: "Your configuration has been updated." });
    setTimeout(() => setSaved(false), 3000);
  };

  const automationLabel = settings.automationLevel[0] <= 25 ? "Manual" :
    settings.automationLevel[0] <= 50 ? "Semi-Auto" :
    settings.automationLevel[0] <= 75 ? "Assisted" : "Fully Autonomous";

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="animate-fade-in flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          </div>
          <p className="text-sm text-muted-foreground mt-1">Configure your Swarm AI event platform</p>
        </div>
        <Button onClick={handleSave} className="gap-2">
          {saved ? <CheckCircle2 className="h-4 w-4" /> : <Save className="h-4 w-4" />}
          {saved ? "Saved" : "Save Changes"}
        </Button>
      </div>

      {/* Event Configuration */}
      <Card className="glass-card animate-fade-in" style={{ animationDelay: "60ms", animationFillMode: "both" }}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <CalendarClock className="h-4 w-4 text-primary" />
            Event Configuration
          </CardTitle>
          <CardDescription>Core event details used across all agents</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="eventName">Event Name</Label>
              <Input id="eventName" value={settings.eventName} onChange={e => update("eventName", e.target.value)} maxLength={100} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="eventDate">Event Date</Label>
              <Input id="eventDate" type="date" value={settings.eventDate} onChange={e => update("eventDate", e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="eventLocation">Location</Label>
              <Input id="eventLocation" value={settings.eventLocation} onChange={e => update("eventLocation", e.target.value)} maxLength={200} />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="eventDesc">Description</Label>
            <Textarea id="eventDesc" value={settings.eventDescription} onChange={e => update("eventDescription", e.target.value)} className="min-h-[80px]" maxLength={1000} />
          </div>
        </CardContent>
      </Card>

      {/* Email Provider */}
      <Card className="glass-card animate-fade-in" style={{ animationDelay: "120ms", animationFillMode: "both" }}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Mail className="h-4 w-4 text-neon-cyan" />
            Email Configuration
          </CardTitle>
          <CardDescription>Email provider and sending preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Email Provider</Label>
              <Select value={settings.emailProvider} onValueChange={v => update("emailProvider", v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="lovable">Lovable Cloud (Built-in)</SelectItem>
                  <SelectItem value="resend">Resend</SelectItem>
                  <SelectItem value="sendgrid">SendGrid</SelectItem>
                  <SelectItem value="ses">Amazon SES</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="emailFrom">From Name</Label>
              <Input id="emailFrom" value={settings.emailFromName} onChange={e => update("emailFromName", e.target.value)} maxLength={100} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="emailReply">Reply-To Email</Label>
              <Input id="emailReply" type="email" value={settings.emailReplyTo} onChange={e => update("emailReplyTo", e.target.value)} maxLength={255} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="emailLimit">Daily Send Limit</Label>
              <Input id="emailLimit" type="number" value={settings.emailDailyLimit} onChange={e => update("emailDailyLimit", e.target.value)} min="0" max="10000" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Social Media Integrations */}
      <Card className="glass-card animate-fade-in" style={{ animationDelay: "180ms", animationFillMode: "both" }}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Share2 className="h-4 w-4 text-neon-rose" />
            Social Media Integrations
          </CardTitle>
          <CardDescription>Connect your social accounts for automated posting</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Twitter */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-neon-cyan/10"><Globe className="h-4 w-4 text-neon-cyan" /></div>
              <div>
                <p className="text-sm font-medium">Twitter / X</p>
                <p className="text-xs text-muted-foreground">Post updates and engage with attendees</p>
              </div>
            </div>
            <Switch checked={settings.twitterEnabled} onCheckedChange={v => update("twitterEnabled", v)} />
          </div>
          {settings.twitterEnabled && (
            <div className="ml-12 space-y-2">
              <Label htmlFor="twHandle">Handle</Label>
              <Input id="twHandle" value={settings.twitterHandle} onChange={e => update("twitterHandle", e.target.value)} placeholder="@handle" maxLength={50} />
            </div>
          )}

          <Separator />

          {/* LinkedIn */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-neon-purple/10"><Globe className="h-4 w-4 text-neon-purple" /></div>
              <div>
                <p className="text-sm font-medium">LinkedIn</p>
                <p className="text-xs text-muted-foreground">Professional network promotion</p>
              </div>
            </div>
            <Switch checked={settings.linkedinEnabled} onCheckedChange={v => update("linkedinEnabled", v)} />
          </div>
          {settings.linkedinEnabled && (
            <div className="ml-12 space-y-2">
              <Label htmlFor="liPage">Company Page</Label>
              <Input id="liPage" value={settings.linkedinPage} onChange={e => update("linkedinPage", e.target.value)} placeholder="company-page" maxLength={100} />
            </div>
          )}

          <Separator />

          {/* Instagram */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-neon-rose/10"><Globe className="h-4 w-4 text-neon-rose" /></div>
              <div>
                <p className="text-sm font-medium">Instagram</p>
                <p className="text-xs text-muted-foreground">Visual content and stories</p>
              </div>
            </div>
            <Switch checked={settings.instagramEnabled} onCheckedChange={v => update("instagramEnabled", v)} />
          </div>
          {settings.instagramEnabled && (
            <div className="ml-12 space-y-2">
              <Label htmlFor="igHandle">Handle</Label>
              <Input id="igHandle" value={settings.instagramHandle} onChange={e => update("instagramHandle", e.target.value)} placeholder="@handle" maxLength={50} />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Notification Preferences */}
      <Card className="glass-card animate-fade-in" style={{ animationDelay: "240ms", animationFillMode: "both" }}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Bell className="h-4 w-4 text-neon-amber" />
            Notification Preferences
          </CardTitle>
          <CardDescription>Choose which events trigger organizer notifications</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { key: "notifyEmail" as const, label: "Email campaign completions", desc: "When bulk sends finish or fail" },
            { key: "notifyScheduleChanges" as const, label: "Schedule changes", desc: "When sessions are rescheduled or relocated" },
            { key: "notifyCrisisAlerts" as const, label: "Crisis alerts", desc: "Immediate notification for crisis events" },
            { key: "notifyAgentErrors" as const, label: "Agent errors", desc: "When an AI agent encounters a failure" },
            { key: "notifyRegistrations" as const, label: "New registrations", desc: "Each time a participant registers" },
          ].map(item => (
            <div key={item.key} className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </div>
              <Switch checked={settings[item.key]} onCheckedChange={v => update(item.key, v)} />
            </div>
          ))}
          <Separator />
          <div className="space-y-2">
            <Label>Digest Frequency</Label>
            <Select value={settings.notifyDigestFrequency} onValueChange={v => update("notifyDigestFrequency", v)}>
              <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="realtime">Real-time</SelectItem>
                <SelectItem value="hourly">Hourly</SelectItem>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Agent Automation */}
      <Card className="glass-card animate-fade-in" style={{ animationDelay: "300ms", animationFillMode: "both" }}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Bot className="h-4 w-4 text-neon-green" />
            Agent Automation Level
          </CardTitle>
          <CardDescription>Control how autonomously agents operate</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Global slider */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Global Automation Level</Label>
              <Badge variant="secondary" className="font-mono text-xs">{automationLabel} ({settings.automationLevel[0]}%)</Badge>
            </div>
            <Slider
              value={settings.automationLevel}
              onValueChange={v => update("automationLevel", v)}
              max={100}
              step={5}
              className="py-2"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>Manual</span>
              <span>Semi-Auto</span>
              <span>Assisted</span>
              <span>Autonomous</span>
            </div>
          </div>

          <Separator />

          {/* Per-agent toggles */}
          <div className="space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Per-Agent Auto-Execute</p>
            {[
              { key: "autoSchedule" as const, label: "Scheduler Agent", desc: "Auto-resolve scheduling conflicts" },
              { key: "autoEmail" as const, label: "Email Agent", desc: "Auto-send personalized campaigns" },
              { key: "autoSocial" as const, label: "Content Agent", desc: "Auto-publish social media posts" },
              { key: "autoCrisis" as const, label: "Crisis Agent", desc: "Auto-respond to event disruptions" },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">{item.label}</p>
                  <p className="text-xs text-muted-foreground">{item.desc}</p>
                </div>
                <Switch checked={settings[item.key]} onCheckedChange={v => update(item.key, v)} />
              </div>
            ))}
          </div>

          <Separator />

          <div className="space-y-2">
            <Label>Max Concurrent Agents</Label>
            <Select value={settings.agentConcurrency} onValueChange={v => update("agentConcurrency", v)}>
              <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1</SelectItem>
                <SelectItem value="2">2</SelectItem>
                <SelectItem value="4">4</SelectItem>
                <SelectItem value="8">8</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Bottom save */}
      <div className="flex justify-end pb-8">
        <Button onClick={handleSave} className="gap-2">
          {saved ? <CheckCircle2 className="h-4 w-4" /> : <Save className="h-4 w-4" />}
          {saved ? "Saved" : "Save All Settings"}
        </Button>
      </div>
    </div>
  );
};

export default SettingsPage;
