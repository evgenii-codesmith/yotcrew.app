"use client"

import { useState } from "react"
import Image from "next/image"
import { Search, MapPin, DollarSign, Clock, Building2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"

// Mock job data
const jobs = [
  {
    id: 1,
    title: "Captain",
    company: "Luxury Yacht Charter",
    location: "Monaco",
    salary: "€8,000 - €12,000/month",
    type: "Full-time",
    vesselSize: "50-74m",
    department: "Deck",
    vesselType: "Motor",
    description:
      "Experienced Captain needed for 65m motor yacht. Must have MCA certification and Mediterranean experience.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "2 days ago",
  },
  {
    id: 2,
    title: "Chief Engineer",
    company: "Private Yacht Owner",
    location: "Fort Lauderdale, FL",
    salary: "$7,000 - $10,000/month",
    type: "Full-time",
    vesselSize: "40-49m",
    department: "Engineering",
    vesselType: "Motor",
    description: "Chief Engineer position on 45m private motor yacht. Caterpillar engine experience preferred.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "1 day ago",
  },
  {
    id: 3,
    title: "Chef",
    company: "Superyacht Management",
    location: "Antibes, France",
    salary: "€5,000 - €7,500/month",
    type: "Full-time",
    vesselSize: "75+",
    department: "Galley",
    vesselType: "Motor",
    description:
      "Talented Chef required for 85m superyacht. Fine dining experience and dietary restrictions knowledge essential.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "3 days ago",
  },
  {
    id: 4,
    title: "First Officer",
    company: "Charter Fleet",
    location: "Caribbean",
    salary: "$4,500 - $6,500/month",
    type: "Full-time",
    vesselSize: "31-39m",
    department: "Deck",
    vesselType: "Sail",
    description: "First Officer needed for 35m sailing yacht in Caribbean charter fleet. RYA Yachtmaster required.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "1 week ago",
  },
  {
    id: 5,
    title: "Second Engineer",
    company: "Yacht Services Inc",
    location: "Palma, Spain",
    salary: "€4,000 - €5,500/month",
    type: "Full-time",
    vesselSize: "50-74m",
    department: "Engineering",
    vesselType: "Motor",
    description:
      "Second Engineer position on 60m motor yacht. MTU engine experience and electrical knowledge required.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "4 days ago",
  },
  {
    id: 6,
    title: "Deckhand",
    company: "Mediterranean Charters",
    location: "Nice, France",
    salary: "€2,500 - €3,500/month",
    type: "Full-time",
    vesselSize: "0-30m",
    department: "Deck",
    vesselType: "Motor",
    description: "Entry-level Deckhand position on 28m charter yacht. Great opportunity to start your yachting career.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "5 days ago",
  },
  {
    id: 7,
    title: "Bosun",
    company: "Private Owner",
    location: "Newport, RI",
    salary: "$5,000 - $7,000/month",
    type: "Full-time",
    vesselSize: "40-49m",
    department: "Deck",
    vesselType: "Sail",
    description: "Experienced Bosun needed for 42m sailing yacht. Must have strong leadership and maintenance skills.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "6 days ago",
  },
  {
    id: 8,
    title: "Sous Chef",
    company: "Yacht Crew Agency",
    location: "Barcelona, Spain",
    salary: "€3,500 - €4,500/month",
    type: "Part-time",
    vesselSize: "31-39m",
    department: "Galley",
    vesselType: "Motor",
    description: "Sous Chef position for busy charter season. Mediterranean cuisine experience preferred.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "1 week ago",
  },
  {
    id: 9,
    title: "ETO (Electro Technical Officer)",
    company: "Superyacht Fleet",
    location: "Miami, FL",
    salary: "$6,000 - $8,500/month",
    type: "Full-time",
    vesselSize: "75+",
    department: "Engineering",
    vesselType: "Motor",
    description: "ETO needed for 90m superyacht with advanced systems. STCW and electronics expertise required.",
    logo: "/placeholder.svg?height=60&width=60",
    posted: "3 days ago",
  },
]

export default function Component() {
  const [currentPage, setCurrentPage] = useState(1)
  const jobsPerPage = 6
  const totalPages = Math.ceil(jobs.length / jobsPerPage)

  const startIndex = (currentPage - 1) * jobsPerPage
  const currentJobs = jobs.slice(startIndex, startIndex + jobsPerPage)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" />
                  <path d="M4 14L6 18H18L20 14L18 12H6L4 14Z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-gray-900">Yotcrew.app</h1>
            </div>
            <Button>Post a Job</Button>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div className="lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input placeholder="Search yacht crew positions..." className="pl-10" />
              </div>
            </div>

            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Job Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="full-time">Full-time</SelectItem>
                <SelectItem value="part-time">Part-time</SelectItem>
                <SelectItem value="contract">Contract</SelectItem>
                <SelectItem value="freelance">Freelance</SelectItem>
              </SelectContent>
            </Select>

            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Location" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Locations</SelectItem>
                <SelectItem value="remote">Remote</SelectItem>
                <SelectItem value="san-francisco">San Francisco</SelectItem>
                <SelectItem value="new-york">New York</SelectItem>
                <SelectItem value="austin">Austin</SelectItem>
                <SelectItem value="seattle">Seattle</SelectItem>
              </SelectContent>
            </Select>

            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Vessel Size" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sizes</SelectItem>
                <SelectItem value="0-30m">0-30m</SelectItem>
                <SelectItem value="31-39m">31-39m</SelectItem>
                <SelectItem value="40-49m">40-49m</SelectItem>
                <SelectItem value="50-74m">50-74m</SelectItem>
                <SelectItem value="75+">75m+</SelectItem>
              </SelectContent>
            </Select>

            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                <SelectItem value="deck">Deck</SelectItem>
                <SelectItem value="engineering">Engineering</SelectItem>
                <SelectItem value="galley">Galley</SelectItem>
              </SelectContent>
            </Select>

            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Vessel Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="motor">Motor</SelectItem>
                <SelectItem value="sail">Sail</SelectItem>
              </SelectContent>
            </Select>

            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Newest</SelectItem>
                <SelectItem value="oldest">Oldest</SelectItem>
                <SelectItem value="salary-high">Salary: High to Low</SelectItem>
                <SelectItem value="salary-low">Salary: Low to High</SelectItem>
                <SelectItem value="relevance">Relevance</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <p className="text-gray-600">
            Showing {startIndex + 1}-{Math.min(startIndex + jobsPerPage, jobs.length)} of {jobs.length} jobs
          </p>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">View:</span>
            <Button variant="outline" size="sm">
              Grid
            </Button>
            <Button variant="ghost" size="sm">
              List
            </Button>
          </div>
        </div>

        {/* Job Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {currentJobs.map((job) => (
            <Card key={job.id} className="hover:shadow-lg transition-shadow duration-200">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <Image
                      src={job.logo || "/placeholder.svg"}
                      alt={`${job.company} logo`}
                      width={48}
                      height={48}
                      className="rounded-lg"
                    />
                    <div>
                      <h3 className="font-semibold text-lg leading-tight">{job.title}</h3>
                      <p className="text-gray-600 flex items-center gap-1">
                        <Building2 className="h-4 w-4" />
                        {job.company}
                      </p>
                    </div>
                  </div>
                  <Badge variant={job.type === "Full-time" ? "default" : "secondary"}>{job.type}</Badge>
                </div>
              </CardHeader>

              <CardContent className="pb-4">
                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MapPin className="h-4 w-4" />
                    {job.location}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <DollarSign className="h-4 w-4" />
                    {job.salary}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Clock className="h-4 w-4" />
                    {job.posted}
                  </div>
                </div>

                <p className="text-gray-700 text-sm line-clamp-3">{job.description}</p>

                <div className="mt-3 flex gap-2 flex-wrap">
                  <Badge variant="outline">{job.vesselSize}</Badge>
                  <Badge variant="outline">{job.department}</Badge>
                  <Badge variant="outline">{job.vesselType}</Badge>
                </div>
              </CardContent>

              <CardFooter className="pt-0">
                <div className="flex gap-2 w-full">
                  <Button className="flex-1">Apply Now</Button>
                  <Button variant="outline" size="icon">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                      />
                    </svg>
                  </Button>
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Pagination */}
        <div className="flex justify-center">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  href="#"
                  onClick={(e) => {
                    e.preventDefault()
                    if (currentPage > 1) setCurrentPage(currentPage - 1)
                  }}
                  className={currentPage === 1 ? "pointer-events-none opacity-50" : ""}
                />
              </PaginationItem>

              {[...Array(totalPages)].map((_, i) => (
                <PaginationItem key={i + 1}>
                  <PaginationLink
                    href="#"
                    onClick={(e) => {
                      e.preventDefault()
                      setCurrentPage(i + 1)
                    }}
                    isActive={currentPage === i + 1}
                  >
                    {i + 1}
                  </PaginationLink>
                </PaginationItem>
              ))}

              <PaginationItem>
                <PaginationNext
                  href="#"
                  onClick={(e) => {
                    e.preventDefault()
                    if (currentPage < totalPages) setCurrentPage(currentPage + 1)
                  }}
                  className={currentPage === totalPages ? "pointer-events-none opacity-50" : ""}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      </main>
    </div>
  )
}
