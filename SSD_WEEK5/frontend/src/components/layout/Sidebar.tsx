import { Link, useLocation } from "react-router-dom";
import { File, Globe, Mail, Search, Shield, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Sidebar as SidebarComponent,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

// Menu items for the sidebar
const toolItems = [
  {
    title: "Overview",
    path: "/dashboard",
    icon: Search,
  },
  {
    title: "Social Media",
    path: "/dashboard/social",
    icon: Users,
  },
  {
    title: "IP & Domain",
    path: "/dashboard/ip-domain",
    icon: Globe,
  },
  {
    title: "Email & Phone",
    path: "/dashboard/email-phone",
    icon: Mail,
  },
  {
    title: "Web Scraping",
    path: "/dashboard/web-scraping",
    icon: File,
  },
  {
    title: "Secure Reporting",
    path: "/dashboard/reporting",
    icon: Shield,
  },
];

export function Sidebar({ isMobile = false }: { isMobile?: boolean }) {
  const location = useLocation();

  return (
    <SidebarComponent
      className={cn(
        "border-r bg-sidebar fixed inset-y-0 z-30 hidden md:flex flex-col",
        isMobile && "flex fixed md:hidden"
      )}
    >
      <SidebarContent className="pt-16">
        <SidebarGroup>
          <SidebarGroupLabel>Dashboard</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {toolItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={location.pathname === item.path}
                  >
                    <Link to={item.path}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </SidebarComponent>
  );
}
